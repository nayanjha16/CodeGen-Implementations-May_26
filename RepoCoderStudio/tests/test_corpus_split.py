from pathlib import Path

import faiss
import numpy as np

from src.corpus_retriever import CorpusIndex


class Storage:
    def __init__(self, root: Path, rows):
        self.root = root
        self.rows = rows

    def approved_corpus_path(self):
        return "approved.jsonl"

    def exists(self, _path):
        return True

    def load_jsonl(self, _path):
        return self.rows


def test_corpus_index_loads_train_only(tmp_path):
    index = CorpusIndex.__new__(CorpusIndex)
    index.storage = Storage(
        tmp_path,
        [
            {"corpus_id": "a", "provenance": {"split": "train"}},
            {"corpus_id": "b", "provenance": {"split": "test"}},
            {"corpus_id": "c", "provenance": {"split": "validation"}},
        ],
    )
    rows = index._load_train_rows()
    assert [row["corpus_id"] for row in rows] == ["a"]


def test_has_java_flags_only_rows_with_java_code():
    assert CorpusIndex._has_java({"java_code": "class X {}"})
    assert not CorpusIndex._has_java({"java_code": ""})
    assert not CorpusIndex._has_java({"java_code": "   "})
    assert not CorpusIndex._has_java({})


class _FixedEmbedder:
    """Returns a pre-registered vector per query text -- avoids needing a
    real sentence-transformers model for this dependency-light test."""

    def __init__(self, vectors_by_query):
        self._vectors_by_query = vectors_by_query

    def encode_query(self, query: str) -> np.ndarray:
        return self._vectors_by_query[query]


def test_search_field_routes_to_the_matching_index():
    # Two rows: one Python-only, one with a Java translation. NL and Python
    # query keys cover both rows; Java is a strict subset.
    rows = [
        {"corpus_id": "py_only", "natural_language": "add two numbers", "python_code": "def add(a, b): return a + b", "java_code": ""},
        {"corpus_id": "has_java", "natural_language": "flag a transaction", "python_code": "def flag(x): return x", "java_code": "class Flag {}"},
    ]
    index = CorpusIndex.__new__(CorpusIndex)
    index._rows = rows
    index._java_rows = [r for r in rows if CorpusIndex._has_java(r)]
    assert [r["corpus_id"] for r in index._java_rows] == ["has_java"]

    dim = 4
    python_vectors = np.eye(dim, dtype=np.float32)[: len(rows)]
    java_vectors = np.eye(dim, dtype=np.float32)[len(rows) : len(rows) + len(index._java_rows)]

    index.index = faiss.IndexFlatIP(dim)
    index.index.add(python_vectors)
    index.nl_index = faiss.IndexFlatIP(dim)
    index.nl_index.add(python_vectors)
    index.java_index = faiss.IndexFlatIP(dim)
    index.java_index.add(java_vectors)

    index.embedder = _FixedEmbedder(
        {
            "python query": python_vectors[0],
            "nl query": python_vectors[1],
            "java query": java_vectors[0],
        }
    )

    python_results = index.search("python query", top_k=2, field="python")
    assert python_results[0].name  # non-empty title
    assert python_results[0].source_preview == "def add(a, b): return a + b"
    assert python_results[0].java_preview == ""  # py_only row has no java_code

    nl_results = index.search("nl query", top_k=2, field="nl")
    assert nl_results[0].source_preview == "def flag(x): return x"
    assert nl_results[0].java_preview == "class Flag {}"

    java_results = index.search("java query", top_k=2, field="java")
    assert java_results[0].source_preview == "class Flag {}"
    assert java_results[0].java_preview == ""  # java-field results don't reuse this slot
    assert java_results[0].python_preview == "def flag(x): return x"
    assert java_results[0].provenance == "validated_train_corpus"
