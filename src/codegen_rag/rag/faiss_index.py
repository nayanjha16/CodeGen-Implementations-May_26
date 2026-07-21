"""Dense (token-embedding) retrieval over a FAISS index.

Per the proposal: "codegen-350M-multi encoder outputs indexed in FAISS
IndexIVFFlat. Top-K cosine similarity search with K tested at 1, 3, 5, and 10."
IVF requires enough training vectors to be meaningful (FAISS recommends >=39
points per cluster); for small corpora (e.g. unit tests, or an early
Checkpoint-3 smoke test with <500 samples) this automatically falls back to
an exact flat index rather than raising or silently training garbage
clusters — the fallback is logged so it's never silently different behavior.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


class CodeSearchIndex:
    """FAISS-backed cosine-similarity search over code-chunk embeddings."""

    def __init__(self, dim: int, use_ivf: bool = True, nlist: int = 100):
        self.dim = dim
        self.use_ivf = use_ivf
        self.nlist = nlist
        self._index: Any = None
        self.id_to_metadata: dict[int, dict[str, Any]] = {}
        self._next_id = 0
        self.used_ivf: bool = False

    def build(self, embeddings: np.ndarray, metadata: list[dict[str, Any]]) -> None:
        """(Re)build the index from scratch over a full embedding matrix."""
        import faiss

        if embeddings.shape[0] != len(metadata):
            raise ValueError("embeddings and metadata must have the same length")

        vectors = np.ascontiguousarray(embeddings.astype("float32"))
        faiss.normalize_L2(vectors)

        n = vectors.shape[0]
        quantizer = faiss.IndexFlatIP(self.dim)
        effective_nlist = min(self.nlist, max(1, n // 39))

        if self.use_ivf and effective_nlist >= 2 and n >= effective_nlist * 39:
            base_index = faiss.IndexIVFFlat(quantizer, self.dim, effective_nlist, faiss.METRIC_INNER_PRODUCT)
            base_index.train(vectors)
            base_index.nprobe = min(effective_nlist, 10)
            self.used_ivf = True
            logger.info("Built IndexIVFFlat with nlist=%d over %d vectors", effective_nlist, n)
        else:
            base_index = quantizer
            self.used_ivf = False
            logger.info(
                "Corpus too small for IVF training (n=%d); using exact IndexFlatIP instead", n
            )

        self._index = faiss.IndexIDMap(base_index)
        ids = np.arange(n, dtype=np.int64)
        self._index.add_with_ids(vectors, ids)
        self.id_to_metadata = {int(i): m for i, m in zip(ids, metadata, strict=True)}
        self._next_id = n

    def add(self, embeddings: np.ndarray, metadata: list[dict[str, Any]]) -> None:
        """Append more vectors to an already-built index (no retraining)."""
        import faiss

        if self._index is None:
            self.build(embeddings, metadata)
            return

        vectors = np.ascontiguousarray(embeddings.astype("float32"))
        faiss.normalize_L2(vectors)
        ids = np.arange(self._next_id, self._next_id + len(metadata), dtype=np.int64)
        self._index.add_with_ids(vectors, ids)
        for i, m in zip(ids, metadata, strict=True):
            self.id_to_metadata[int(i)] = m
        self._next_id += len(metadata)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict[str, Any]]:
        import faiss

        if self._index is None:
            raise RuntimeError("Index has not been built yet — call build() first")

        query = np.ascontiguousarray(query_embedding.astype("float32")).reshape(1, -1)
        faiss.normalize_L2(query)
        scores, ids = self._index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], ids[0], strict=True):
            if idx == -1:
                continue
            results.append({"score": float(score), "chunk_id": int(idx), **self.id_to_metadata[int(idx)]})
        return results

    def save(self, path: Path) -> None:
        import faiss

        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path / "index.faiss"))
        with open(path / "metadata.pkl", "wb") as fh:
            pickle.dump(self.id_to_metadata, fh)
        with open(path / "config.json", "w", encoding="utf-8") as fh:
            json.dump(
                {"dim": self.dim, "use_ivf": self.use_ivf, "nlist": self.nlist, "next_id": self._next_id},
                fh,
            )
        logger.info("Saved FAISS index (%d vectors) to %s", self._next_id, path)

    @classmethod
    def load(cls, path: Path) -> "CodeSearchIndex":
        import faiss

        with open(path / "config.json", encoding="utf-8") as fh:
            cfg = json.load(fh)
        instance = cls(dim=cfg["dim"], use_ivf=cfg["use_ivf"], nlist=cfg["nlist"])
        instance._index = faiss.read_index(str(path / "index.faiss"))
        with open(path / "metadata.pkl", "rb") as fh:
            instance.id_to_metadata = pickle.load(fh)
        instance._next_id = cfg["next_id"]
        return instance

    def __len__(self) -> int:
        return self._next_id
