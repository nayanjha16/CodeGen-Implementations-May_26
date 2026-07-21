"""Hybrid retrieval: fuse dense (FAISS) and AST-based rankings via Reciprocal
Rank Fusion (RRF) rather than a raw score blend, since dense cosine scores and
AST Jaccard scores live on different scales and RRF is scale-invariant.
"""

from __future__ import annotations

from typing import Any

from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def reciprocal_rank_fusion(
    result_lists: list[list[dict[str, Any]]],
    key: str = "chunk_id",
    k: int = 60,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Standard RRF: score(d) = sum over lists of 1 / (k + rank_in_list(d)).

    ``k=60`` is the value from the original RRF paper and is a reasonable
    default that de-emphasizes any single retriever's top pick from
    dominating the fused ranking.
    """
    fused_scores: dict[Any, float] = {}
    item_by_key: dict[Any, dict[str, Any]] = {}

    for results in result_lists:
        for rank, item in enumerate(results):
            item_id = item[key]
            fused_scores[item_id] = fused_scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
            item_by_key.setdefault(item_id, item)

    ranked_ids = sorted(fused_scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]
    return [{**item_by_key[item_id], "fusion_score": score} for item_id, score in ranked_ids]


class HybridRetriever:
    """Combines a `CodeSearchIndex` (dense) and an `ASTRetrievalIndex`
    (structural) over the same underlying corpus. Both indexes must have been
    built with metadata sharing a common ``chunk_id`` for fusion to work.
    """

    def __init__(self, dense_index: CodeSearchIndex, ast_index: ASTRetrievalIndex, rrf_k: int = 60):
        self.dense_index = dense_index
        self.ast_index = ast_index
        self.rrf_k = rrf_k

    def search(self, query_code: str, query_embedding, top_k: int = 5) -> list[dict[str, Any]]:
        dense_results = self.dense_index.search(query_embedding, top_k=top_k * 3)
        ast_results = self.ast_index.search(query_code, top_k=top_k * 3)
        fused = reciprocal_rank_fusion(
            [dense_results, ast_results], key="chunk_id", k=self.rrf_k, top_k=top_k
        )
        logger.debug("Hybrid retrieval: %d dense + %d ast -> %d fused", len(dense_results), len(ast_results), len(fused))
        return fused
