"""Hybrid BM25 + dense retriever for RAG references (plan §7, SPEC §10 step 7).

At training and inference a *reference example* is pasted into the prompt to help
the model generalise. References are retrieved from a **train-only** index
(building it from dev would leak) by a hybrid of BM25 (lexical) and dense cosine
(``BAAI/bge-small-en-v1.5``), restricted to the **same ``db_id``** so the
reference's schema is relevant.

**Self-exclusion by ``uid`` is load-bearing, not decorative (SPEC-REVIEW #5).**
During failure mining (step 11) inference runs *on the train split* against this
*train-built* index, so an example's own twin sits in the index. If it retrieved
itself it would paste the gold answer into its own prompt, inflate Pass-1 train
accuracy, and shrink the mined failure set that feeds the teacher. Every
retrieval path therefore drops candidates whose ``uid`` equals the query's.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from . import config
from .device import get_device
from .loader import Example

log = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_MODEL_CACHE: dict[str, object] = {}


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _embeddings_path(task: str) -> Path:
    return config.RETRIEVAL_INDEX_DIR / f"{task}_embeddings.npy"


def _metadata_path(task: str) -> Path:
    return config.RETRIEVAL_INDEX_DIR / f"{task}_metadata.json"


def get_embedder():
    """Load (and cache) the sentence-transformers embedding model on MPS."""
    from sentence_transformers import SentenceTransformer

    name = config.CONFIG.rag.embedding_model
    if name not in _MODEL_CACHE:
        device = get_device().type
        log.info("loading embedder %s on %s", name, device)
        _MODEL_CACHE[name] = SentenceTransformer(name, device=device)
    return _MODEL_CACHE[name]


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed and L2-normalise a list of texts (cosine == dot product)."""
    model = get_embedder()
    emb = model.encode(
        texts,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return emb.astype(np.float32)


def index_exists(task: str) -> bool:
    return _embeddings_path(task).exists() and _metadata_path(task).exists()


def _minmax(x: np.ndarray) -> np.ndarray:
    """Scale to [0,1]; a degenerate (all-equal) vector maps to all-zeros."""
    if x.size == 0:
        return x
    lo, hi = float(x.min()), float(x.max())
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


class Retriever:
    """In-memory hybrid retriever for one task's train-only index."""

    def __init__(self, task: str):
        if not index_exists(task):
            raise FileNotFoundError(
                f"retrieval index for {task!r} missing — run scripts/build_retrieval_index.py"
            )
        self.task = task
        self.embeddings: np.ndarray = np.load(_embeddings_path(task))
        self.meta: list[dict] = json.loads(_metadata_path(task).read_text(encoding="utf-8"))
        if len(self.meta) != self.embeddings.shape[0]:
            raise ValueError(f"{task}: metadata/embeddings length mismatch")

        # db_id -> row indices, and a global BM25 over input texts.
        self.by_db: dict[str, list[int]] = {}
        for i, m in enumerate(self.meta):
            self.by_db.setdefault(m["db_id"], []).append(i)
        self._uid_to_row = {m["uid"]: i for i, m in enumerate(self.meta)}
        self._corpus_tokens = [_tokenize(m["input_text"]) for m in self.meta]
        self._bm25 = BM25Okapi(self._corpus_tokens) if self._corpus_tokens else None

    def _to_example(self, m: dict) -> Example:
        """Reconstruct a minimal reference Example (only input + gold are used)."""
        is_sql_input = self.task == "sql2nosql"
        return Example(
            task=self.task,
            source="spider" if self.task == "text2sql" else "docspider",
            split="train",
            db_id=m["db_id"],
            question=None if is_sql_input else m["input_text"],
            source_sql=m["input_text"] if is_sql_input else None,
            gold=m["gold"],
            schema="",  # not used when this Example is a reference
            difficulty=None,
            origin_index=-1,
        )

    def retrieve(
        self,
        query_text: str,
        db_id: str,
        exclude_uid: str | None = None,
        top_k: int = 1,
        query_embedding: np.ndarray | None = None,
    ) -> list[Example]:
        """Return up to ``top_k`` same-``db_id`` references, self excluded by uid."""
        candidates = [
            i for i in self.by_db.get(db_id, [])
            if exclude_uid is None or self.meta[i]["uid"] != exclude_uid
        ]
        if not candidates:
            return []

        cand = np.array(candidates)
        # Dense score: reuse the stored embedding if the query is in the index
        # (train-time), else embed on the fly (dev-time).
        if query_embedding is None:
            row = self._uid_to_row.get(exclude_uid) if exclude_uid else None
            if row is not None:
                query_embedding = self.embeddings[row]
            else:
                query_embedding = embed_texts([query_text])[0]
        dense = self.embeddings[cand] @ query_embedding  # cosine (normalised)

        # Lexical score over the same candidates.
        if self._bm25 is not None:
            bm25_all = np.asarray(self._bm25.get_scores(_tokenize(query_text)))
            bm25 = bm25_all[cand]
        else:
            bm25 = np.zeros(len(cand), dtype=np.float32)

        hybrid = _minmax(dense) + _minmax(bm25)
        order = np.argsort(-hybrid)[:top_k]
        return [self._to_example(self.meta[int(cand[j])]) for j in order]

    def retrieve_for(self, example: Example, top_k: int = 1) -> list[Example]:
        """Retrieve references for an Example, excluding its own twin by uid."""
        from .prompt_builder import input_value

        return self.retrieve(
            query_text=input_value(example),
            db_id=example.db_id,
            exclude_uid=example.uid,
            top_k=top_k,
        )


_RETRIEVER_CACHE: dict[str, Retriever] = {}


def get_retriever(task: str) -> Retriever:
    """Cached per-task retriever."""
    if task not in _RETRIEVER_CACHE:
        _RETRIEVER_CACHE[task] = Retriever(task)
    return _RETRIEVER_CACHE[task]
