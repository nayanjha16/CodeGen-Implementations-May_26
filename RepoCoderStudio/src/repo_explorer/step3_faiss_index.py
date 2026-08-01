"""
============================================================
RepoCoder Studio — Stage 4
step3_faiss_index.py
============================================================

FAISS index construction and the natural-language code search engine.

NOTE: Reconstructed from the Stage 4 documentation — see step1_ast_parser.py
for the reconstruction disclaimer, which applies to this whole package.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

COMPONENT_KINDS = ("function", "class", "module")


@dataclass
class SearchResult:
    rank: int
    score: float
    component_type: str
    name: str
    file_path: str
    start_line: Optional[int]
    docstring: str
    signature: str
    source_preview: str
    # Only set by CorpusIndex (src/corpus_retriever.py). These preserve the
    # paired target modality for translation prompts: Python-index results
    # can expose their Java translation (T2/T3), while Java-index results
    # can expose their paired Python translation (T4).
    java_preview: str = ""
    python_preview: str = ""
    dense_score: Optional[float] = None
    lexical_score: Optional[float] = None
    reranker_score: Optional[float] = None
    retrieval_method: str = "dense"
    provenance: str = "repository"


class FAISSIndexBuilder:
    """Builds/loads FAISS indices for each component type."""

    def __init__(self, embedding_dir: str):
        self.embedding_dir = Path(embedding_dir)
        self.indices: Dict[str, "faiss.Index"] = {}
        self.metadata: Dict[str, dict] = {}

    def _index_path(self, kind: str) -> Path:
        return self.embedding_dir / f"{kind}_index.faiss"

    def _build_one(self, kind: str) -> None:
        vectors = np.load(self.embedding_dir / f"{kind}_embeddings.npy").astype(np.float32)
        n, dim = vectors.shape if vectors.size else (0, 384)

        if n == 0:
            index = faiss.IndexFlatIP(dim)
        elif n < 1000:
            index = faiss.IndexFlatIP(dim)
            index.add(vectors)
        else:
            nlist = min(int(math.sqrt(n)), 100)
            nprobe = min(nlist, 10)
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist)
            index.train(vectors)
            index.add(vectors)
            index.nprobe = nprobe

        faiss.write_index(index, str(self._index_path(kind)))
        self.indices[kind] = index

        meta_path = self.embedding_dir / f"{kind}_metadata.json"
        self.metadata[kind] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    def build_all_indices(self) -> None:
        for kind in COMPONENT_KINDS:
            self._build_one(kind)

    def load_existing_indices(self) -> None:
        for kind in COMPONENT_KINDS:
            self.indices[kind] = faiss.read_index(str(self._index_path(kind)))
            meta_path = self.embedding_dir / f"{kind}_metadata.json"
            self.metadata[kind] = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}


class CodeSearchEngine:
    """Natural-language search across functions, classes, and modules."""

    def __init__(self, index_builder: FAISSIndexBuilder, embedder):
        self.index_builder = index_builder
        self.embedder = embedder

    def search(
        self,
        query: str,
        top_k: int = 5,
        component_types: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        types = component_types or list(COMPONENT_KINDS)
        query_vec = self.embedder.encode_query(query).astype(np.float32).reshape(1, -1)

        merged: List[SearchResult] = []
        for kind in types:
            index = self.index_builder.indices.get(kind)
            if index is None or index.ntotal == 0:
                continue
            scores, ids = index.search(query_vec, min(top_k, index.ntotal))
            meta = self.index_builder.metadata.get(kind, {})
            for score, idx in zip(scores[0], ids[0]):
                if idx < 0:
                    continue
                entry = meta.get(str(idx), {})
                source_preview = entry.get("source", "") if "source" in entry else ""
                merged.append(
                    SearchResult(
                        rank=0,
                        score=float(score),
                        component_type=kind,
                        name=entry.get("name", "?"),
                        file_path=entry.get("file_path", "?"),
                        start_line=entry.get("start_line"),
                        docstring=entry.get("docstring", ""),
                        signature=entry.get("name", "?"),
                        source_preview=source_preview,
                    )
                )

        merged.sort(key=lambda r: r.score, reverse=True)
        merged = merged[:top_k]
        for i, r in enumerate(merged, start=1):
            r.rank = i
        return merged

    def display_results(self, query: str, results: List[SearchResult]) -> None:
        print(f"Search: '{query}'")
        for r in results:
            print(f"  [{r.rank}] {r.component_type}:{r.name}  score={r.score:.3f}  {r.file_path}")

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        top_k = retrieved[:k]
        if not top_k:
            return 0.0
        hits = sum(1 for r in top_k if r in relevant)
        return hits / len(top_k)

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        if not relevant:
            return 0.0
        top_k = retrieved[:k]
        hits = sum(1 for r in relevant if r in top_k)
        return hits / len(relevant)

    @staticmethod
    def mrr_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
        for i, r in enumerate(retrieved[:k], start=1):
            if r in relevant:
                return 1.0 / i
        return 0.0

    def run_evaluation(self, test_queries: List[dict], k: int = 5) -> dict:
        """test_queries: [{"query": str, "relevant": [names...]}]"""
        precisions, recalls, mrrs = [], [], []
        for tq in test_queries:
            results = self.search(tq["query"], top_k=k)
            retrieved_names = [r.name for r in results]
            relevant = tq.get("relevant", [])
            precisions.append(self.precision_at_k(retrieved_names, relevant, k))
            recalls.append(self.recall_at_k(retrieved_names, relevant, k))
            mrrs.append(self.mrr_at_k(retrieved_names, relevant, k))

        summary = {
            f"avg_precision_at_{k}": sum(precisions) / len(precisions) if precisions else 0.0,
            f"avg_recall_at_{k}": sum(recalls) / len(recalls) if recalls else 0.0,
            f"avg_mrr_at_{k}": sum(mrrs) / len(mrrs) if mrrs else 0.0,
        }
        print("Evaluation:", summary)
        return summary
