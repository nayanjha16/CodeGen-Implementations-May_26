"""
============================================================
RepoCoder Studio
corpus_retriever.py  —  Stage 5 (RAG corpus source)
============================================================

Second retrieval source for Stage 5, alongside Stage 4's repository index
(src/repo_explorer/): a FAISS index built directly over this project's
own approved, validated corpus (outputs/approved_corpus/approved_corpus.jsonl)
-- the corpus Stages 1-3 spent most of their engineering effort proving
trustworthy, and the corpus the T1/T3 evaluation split is scored against.

Why a separate index instead of routing corpus rows through Stage 4's
AST-based RepositoryIndexer: approved-corpus rows are bare XLCoST/CodeXGLUE
solutions (often not wrapped in a named top-level function), so extracting
them via ast.FunctionDef/ClassDef would silently miss most rows. Embedding
the row text directly -- the same thing semantic_alignment_engine.py
already does for cross-language alignment -- is both simpler and more
correct here.

Leakage guard
-------------
Only rows whose provenance.split == "train" are indexed. Both
approved_corpus.jsonl (via provenance.split) and task_dataset.jsonl
(via a top-level split field) already carry this field --
tokenizer_builder.py already filters on it to build train/validation/test
HF datasets. Retrieving from validation/test rows here would let a
RAG-augmented evaluation retrieve the exact answer it is being scored
against, invalidating any "RAG improves Pass@k" result computed from it.
Enforced inside build(), not left to the caller to remember.

SearchResult reuse
-------------------
search() returns src.repo_explorer.step3_faiss_index.SearchResult objects,
the same type Stage 4's CodeSearchEngine returns -- so RetrievalEngine can
merge results from both sources with no special-casing.

Three query-key spaces, one corpus
----------------------------------
Earlier versions concatenated natural language and Python into one embedding.
That made an NL query compete against a mixed NL+code vector and made a Python
query do the same. The improved index stores three independent query keys:

- natural_language for T1/T2;
- python_code for T3/T5;
- java_code for T4/T6.

The retrieved row still carries the paired NL/Python/Java evidence needed by
the target task. Only the ranking key is separated, which improves query-
document modality alignment without indexing validation/test answers.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional

import faiss
import numpy as np

from src.artifact_manifest import (
    atomic_write_json,
    corpus_manifest,
    load_json,
    manifests_compatible,
)
from src.config import CONFIG, AppConfig
from src.logger import LOG
from src.repo_explorer.step2_embeddings import CodeEmbedder
from src.repo_explorer.step3_faiss_index import SearchResult
from src.security import redact_secrets
from src.storage import ProjectStorageManager


class CorpusIndex:
    """FAISS index over approved_corpus.jsonl's train-split rows, embedded
    the same way Stage 4 embeds repository functions."""

    def __init__(self, config: AppConfig = CONFIG, embedder: Optional[CodeEmbedder] = None):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.embedder = embedder or CodeEmbedder(model_name=config.retrieval.embedding_model)
        self.nl_index: Optional["faiss.Index"] = None
        self.index: Optional["faiss.Index"] = None
        self.java_index: Optional["faiss.Index"] = None
        self._rows: List[dict] = []
        self._java_rows: List[dict] = []

    @property
    def _index_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_index.faiss"

    @property
    def _vectors_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_embeddings.npy"

    @property
    def _nl_index_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_nl_index.faiss"

    @property
    def _nl_vectors_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_nl_embeddings.npy"

    @property
    def _metadata_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_index_metadata.json"

    @property
    def _manifest_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_index_manifest.json"

    @property
    def _java_index_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_java_index.faiss"

    @property
    def _java_vectors_path(self) -> Path:
        return self.storage.corpus_index_dir() / "corpus_java_embeddings.npy"

    @staticmethod
    def _has_java(row: dict) -> bool:
        return bool((row.get("java_code") or "").strip())

    def _load_train_rows(self) -> List[dict]:
        rel_path = self.storage.approved_corpus_path()
        if not self.storage.exists(rel_path):
            LOG.warning(
                f"CorpusIndex: {rel_path} not found -- corpus retrieval will be "
                "empty until the corpus-building stages have been run on this "
                "project root."
            )
            return []

        rows = self.storage.load_jsonl(rel_path)
        train_rows = [
            r for r in rows
            if (r.get("provenance") or {}).get("split") == "train"
        ]
        LOG.info(
            f"CorpusIndex: {len(train_rows)}/{len(rows)} approved rows are "
            "train-split and eligible for retrieval (validation/test rows "
            "are excluded so RAG can never retrieve the exact answer an "
            "evaluation run is scoring against)."
        )
        return train_rows

    def build(self, rebuild: bool = False) -> int:
        """Builds (or loads a cached) FAISS index. Returns the number of
        indexed rows -- 0 if the approved corpus doesn't exist yet, which
        callers should treat as "corpus retrieval unavailable", not an error."""
        if self.embedder.is_mock and not self.config.retrieval.allow_mock_embeddings:
            raise RuntimeError(
                "Semantic embedding model unavailable and mock embeddings are disabled "
                "(REPOCODER_ALLOW_MOCK_EMBEDDINGS=false). Refusing to build or load the "
                "corpus retrieval index with mock embeddings -- a mock-embedded index "
                "(or querying a real index with a mock query embedder) would silently "
                "return meaningless 'Validated Example Evidence'."
            )

        corpus_path = self.storage.path(self.storage.approved_corpus_path())
        # _java_index_path.exists() is part of the cache-hit gate, not just the
        # staleness check below: a corpus index built before the Java index
        # existed is treated the same as "no cache at all" and rebuilt fresh,
        # rather than erroring -- self-healing instead of requiring a manual
        # offline rebuild step just to pick up the new index.
        if (
            not rebuild
            and self._index_path.exists()
            and self._nl_index_path.exists()
            and self._metadata_path.exists()
            and self._java_index_path.exists()
        ):
            cached_manifest = load_json(self._manifest_path)
            if not corpus_path.exists() or not cached_manifest:
                raise RuntimeError("Corpus index manifest or approved corpus is missing; rebuild offline.")
            expected = corpus_manifest(
                corpus_path,
                self.config.retrieval.embedding_model,
                self.embedder.dimension,
                int(cached_manifest.get("indexed_rows", -1)),
                self.embedder.is_mock,
            )
            if not manifests_compatible(
                expected,
                cached_manifest,
                (
                    # "indexed_rows" is deliberately excluded: it can only be
                    # validated by re-parsing/re-filtering the whole corpus file,
                    # which corpus_sha256 already does more cheaply and more
                    # completely (any row addition/removal/edit changes the file
                    # hash) -- an indexed_rows check here would either duplicate
                    # that or (if computed from the cached manifest itself, as an
                    # earlier version of this check did) be tautological.
                    "format_version",
                    "corpus_sha256",
                    "split_filter",
                    "embedding_model",
                    "embedding_dimension",
                    "mock_embeddings",
                ),
            ):
                raise RuntimeError("Corpus index is stale or incompatible; rebuild it offline.")
            self.index = faiss.read_index(str(self._index_path))
            self.nl_index = faiss.read_index(str(self._nl_index_path))
            self._rows = json.loads(self._metadata_path.read_text(encoding="utf-8"))
            if self.index.ntotal != len(self._rows):
                raise RuntimeError("Corpus Python FAISS index and metadata row counts differ.")
            if self.nl_index.ntotal != len(self._rows):
                raise RuntimeError("Corpus NL FAISS index and metadata row counts differ.")
            self.java_index = faiss.read_index(str(self._java_index_path))
            self._java_rows = [r for r in self._rows if self._has_java(r)]
            if self.java_index.ntotal != len(self._java_rows):
                raise RuntimeError("Corpus Java FAISS index and Java row count differ.")
            LOG.info(
                f"CorpusIndex: loaded cached NL/Python indexes ({len(self._rows)} rows, "
                f"{len(self._java_rows)} with a Java index) from {self._index_path.parent}"
            )
            return len(self._rows)

        self._rows = self._load_train_rows()
        if not self._rows:
            self.index = None
            self.nl_index = None
            self.java_index = None
            self._java_rows = []
            self.storage.save_json(
                {"indexed_rows": 0, "reason": "approved_corpus.jsonl not found or empty"},
                self.storage.corpus_index_report_path(),
            )
            return 0

        # Redact once, in place, immediately after load -- everything downstream
        # (embedding text, the persisted metadata file, and search()'s previews)
        # reads from these same redacted fields, so a secret pattern in the
        # source corpus can never reach disk or a response unredacted.
        for row in self._rows:
            for field in ("natural_language", "python_code", "java_code"):
                if row.get(field):
                    row[field] = redact_secrets(row[field])

        nl_texts = [r.get("natural_language", "") for r in self._rows]
        python_texts = [r.get("python_code", "") for r in self._rows]
        nl_vectors = self.embedder.encode(nl_texts, is_query=False)
        vectors = self.embedder.encode(python_texts, is_query=False)

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        self.index = index
        nl_index = faiss.IndexFlatIP(nl_vectors.shape[1])
        nl_index.add(nl_vectors)
        self.nl_index = nl_index

        # Third, independent index over rows that actually have a Java
        # translation (see module docstring: "Three query-key spaces").
        # Most XLCoST/CodeXGLUE rows are Python-only, so this is
        # typically a strict subset of self._rows, not a parallel-length one.
        self._java_rows = [r for r in self._rows if self._has_java(r)]
        java_vectors = None
        if self._java_rows:
            java_texts = [r.get("java_code", "") for r in self._java_rows]
            java_vectors = self.embedder.encode(java_texts, is_query=False)
            java_index = faiss.IndexFlatIP(java_vectors.shape[1])
            java_index.add(java_vectors)
            self.java_index = java_index
        else:
            self.java_index = faiss.IndexFlatIP(vectors.shape[1])
            java_vectors = np.zeros((0, vectors.shape[1]), dtype=np.float32)

        index_dir = self.storage.corpus_index_dir()
        index_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="corpus_index_", dir=index_dir) as tmp:
            tmp_dir = Path(tmp)
            staged_index = tmp_dir / self._index_path.name
            staged_vectors = tmp_dir / self._vectors_path.name
            staged_nl_index = tmp_dir / self._nl_index_path.name
            staged_nl_vectors = tmp_dir / self._nl_vectors_path.name
            staged_metadata = tmp_dir / self._metadata_path.name
            staged_java_index = tmp_dir / self._java_index_path.name
            staged_java_vectors = tmp_dir / self._java_vectors_path.name
            faiss.write_index(index, str(staged_index))
            np.save(staged_vectors, vectors)
            faiss.write_index(nl_index, str(staged_nl_index))
            np.save(staged_nl_vectors, nl_vectors)
            atomic_write_json(staged_metadata, self._rows)
            faiss.write_index(self.java_index, str(staged_java_index))
            np.save(staged_java_vectors, java_vectors)
            os.replace(staged_index, self._index_path)
            os.replace(staged_vectors, self._vectors_path)
            os.replace(staged_nl_index, self._nl_index_path)
            os.replace(staged_nl_vectors, self._nl_vectors_path)
            os.replace(staged_metadata, self._metadata_path)
            os.replace(staged_java_index, self._java_index_path)
            os.replace(staged_java_vectors, self._java_vectors_path)
        atomic_write_json(
            self._manifest_path,
            corpus_manifest(
                corpus_path,
                self.config.retrieval.embedding_model,
                vectors.shape[1],
                len(self._rows),
                self.embedder.is_mock,
            ),
        )

        self.storage.save_json(
            {
                "indexed_rows": len(self._rows),
                "java_indexed_rows": len(self._java_rows),
                "query_key_indexes": {
                    "nl": len(self._rows),
                    "python": len(self._rows),
                    "java": len(self._java_rows),
                },
                "mock_embeddings": self.embedder.is_mock,
                "embedding_model": self.config.retrieval.embedding_model,
                "split_filter": "train",
            },
            self.storage.corpus_index_report_path(),
        )
        return len(self._rows)

    def search(self, query: str, top_k: int = 5, field: str = "python") -> List[SearchResult]:
        """Search the query-key index matching the input modality.

        field="nl" is used by T1/T2, field="python" by T3/T5, and
        field="java" by T4/T6. Returned rows still expose all paired
        evidence required by the target task.
        """
        if field not in {"nl", "python", "java"}:
            raise ValueError(f"Unsupported corpus query field: {field!r}")
        index = (
            self.nl_index
            if field == "nl"
            else self.java_index
            if field == "java"
            else self.index
        )
        rows = self._java_rows if field == "java" else self._rows
        if index is None or index.ntotal == 0 or not query.strip():
            return []

        query_vec = self.embedder.encode_query(query).astype(np.float32).reshape(1, -1)
        scores, ids = index.search(query_vec, min(top_k, index.ntotal))

        results: List[SearchResult] = []
        for rank, (score, idx) in enumerate(zip(scores[0], ids[0]), start=1):
            if idx < 0:
                continue
            row = rows[idx]
            results.append(
                SearchResult(
                    rank=rank,
                    score=float(score),
                    component_type="corpus_example",
                    name=_readable_title(row),
                    file_path=f"approved_corpus/{row.get('corpus_id', '?')}",
                    start_line=None,
                    docstring=(row.get("natural_language") or "")[:200],
                    signature=row.get("corpus_id", "?"),
                    # self._rows was redacted once at load time (build()), so no
                    # further redaction is needed here. The Java-field index's
                    # primary evidence IS the Java code. Preserve the paired
                    # Python target in python_preview so T4 (Java -> Python)
                    # receives an actual bilingual translation example instead
                    # of only another same-language Java fragment.
                    source_preview=(row.get("java_code") if field == "java" else row.get("python_code")) or "",
                    java_preview=(row.get("java_code") or "") if field != "java" else "",
                    python_preview=(row.get("python_code") or "") if field == "java" else "",
                    provenance="validated_train_corpus",
                )
            )
        return results


def _readable_title(row: dict, max_len: int = 90) -> str:
    """Human-readable label for a corpus row -- the retrieved-sources panel
    is the most inspectable part of Stage 5, and a raw corpus_id like
    'xlcost_6347b5fff72f6575' tells a reviewer nothing. XLCoST natural
    language descriptions are formatted "<short title> | <fuller
    description>"; the part before '|' is the readable title."""
    text = (row.get("natural_language") or "").strip()
    if not text:
        return row.get("corpus_id", "?")
    title = text.split("|", 1)[0].strip() or text.splitlines()[0].strip()
    if len(title) > max_len:
        title = title[:max_len].rstrip() + "..."
    return title or row.get("corpus_id", "?")
