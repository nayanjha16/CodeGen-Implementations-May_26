"""Dependency-light retrieval scoring, reranking, and RAG abstention."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "code", "does",
    "for", "from", "how", "in", "is", "it", "of", "on", "or", "that",
    "the", "this", "to", "using", "what", "with",
}


def code_tokens(text: str) -> List[str]:
    """Tokenize prose and snake/camel-case identifiers into one vocabulary."""
    expanded = _CAMEL_RE.sub(" ", text or "").replace("_", " ")
    return [
        token.lower()
        for token in _TOKEN_RE.findall(expanded)
        if len(token) > 1 and token.lower() not in _STOP
    ]


def lexical_overlap(query: str, document: str) -> float:
    """IDF-free BM25-like overlap suitable for reranking a small dense pool."""
    query_tokens = code_tokens(query)
    doc_tokens = code_tokens(document)
    if not query_tokens or not doc_tokens:
        return 0.0
    query_set = set(query_tokens)
    frequencies = {token: doc_tokens.count(token) for token in query_set}
    matched = sum(math.log1p(count) for count in frequencies.values() if count)
    normalizer = sum(math.log1p(query_tokens.count(token)) for token in query_set)
    return min(1.0, matched / normalizer) if normalizer else 0.0


def result_text(result) -> str:
    return "\n".join(
        str(value)
        for value in (
            getattr(result, "name", ""),
            getattr(result, "signature", ""),
            getattr(result, "file_path", ""),
            getattr(result, "docstring", ""),
            getattr(result, "source_preview", ""),
            getattr(result, "java_preview", ""),
            getattr(result, "python_preview", ""),
        )
        if value
    )


class OptionalCrossEncoder:
    """Lazy optional reranker; failure preserves deterministic hybrid ranking."""

    def __init__(self, model_name: str):
        self.model_name = (model_name or "").strip()
        self._model = None
        self.error: Optional[str] = None

    @property
    def enabled(self) -> bool:
        return bool(self.model_name)

    def score(self, query: str, results: Sequence) -> Optional[List[float]]:
        if not self.enabled or not results:
            return None
        try:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name)
            raw = self._model.predict([(query, result_text(r)) for r in results])
            values = [float(value) for value in raw]
            if not values:
                return None
            low, high = min(values), max(values)
            if high <= low:
                return [0.5 for _ in values]
            return [(value - low) / (high - low) for value in values]
        except Exception as exc:  # optional model/network/runtime
            self.error = str(exc)
            return None


def hybrid_rerank(
    query: str,
    results: Iterable,
    dense_weight: float,
    lexical_weight: float,
    cross_encoder: Optional[OptionalCrossEncoder] = None,
    reranker_weight: float = 0.0,
) -> List:
    candidates = list(results)
    cross_scores = (
        cross_encoder.score(query, candidates) if cross_encoder is not None else None
    )
    # A misconfiguration (e.g. both weights set to 0 instead of using
    # enable_hybrid_retrieval=false) would otherwise raise ZeroDivisionError
    # on every retrieval call; fall back to dense-only ranking instead, the
    # same effective behaviour as disabling hybrid retrieval.
    base_total = dense_weight + lexical_weight
    if base_total <= 0:
        dense_weight, lexical_weight, base_total = 1.0, 0.0, 1.0
    for index, result in enumerate(candidates):
        dense = float(getattr(result, "score", 0.0))
        lexical = lexical_overlap(query, result_text(result))
        hybrid = (dense_weight * dense + lexical_weight * lexical) / base_total
        final = hybrid
        if cross_scores is not None:
            final = (1.0 - reranker_weight) * hybrid + reranker_weight * cross_scores[index]
        result.dense_score = dense
        result.lexical_score = lexical
        result.reranker_score = cross_scores[index] if cross_scores is not None else None
        result.score = float(final)
        result.retrieval_method = (
            "dense+lexical+cross_encoder"
            if cross_scores is not None
            else "dense+lexical"
        )
    candidates.sort(key=lambda result: result.score, reverse=True)
    for rank, result in enumerate(candidates, start=1):
        result.rank = rank
    return candidates


@dataclass(frozen=True)
class RetrievalDecision:
    use_rag: bool
    reason: str
    top_score: float
    score_margin: float
    result_count: int


def decide_rag(
    results: Sequence,
    min_top_score: float,
    min_score_margin: float,
    allow_ambiguous_multi_source: bool,
) -> RetrievalDecision:
    if not results:
        return RetrievalDecision(False, "no_evidence", 0.0, 0.0, 0)
    ranked = sorted(results, key=lambda result: result.score, reverse=True)
    top = float(ranked[0].score)
    second = float(ranked[1].score) if len(ranked) > 1 else 0.0
    margin = top - second
    if top < min_top_score:
        return RetrievalDecision(False, "top_score_below_threshold", top, margin, len(ranked))
    sources = {getattr(result, "component_type", "") for result in ranked[:2]}
    source_diverse = any("corpus" in source for source in sources) and len(sources) > 1
    if margin < min_score_margin and not (
        allow_ambiguous_multi_source and source_diverse
    ):
        return RetrievalDecision(False, "ambiguous_top_results", top, margin, len(ranked))
    return RetrievalDecision(True, "evidence_accepted", top, margin, len(ranked))
