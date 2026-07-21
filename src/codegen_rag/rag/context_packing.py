"""Context packing / prompt augmentation and adaptive (dynamic) Top-K selection."""

from __future__ import annotations

from typing import Any


def pack_context(
    retrieved_chunks: list[dict[str, Any]],
    max_chars: int = 2000,
    code_key: str = "code",
) -> str:
    """Concatenate retrieved chunks into a token-budget-aware context prefix.

    Chunks are added in ranked order until ``max_chars`` would be exceeded,
    so the highest-scoring retrievals are always included even when the
    budget can't fit everything.
    """
    parts: list[str] = []
    total = 0
    for chunk in retrieved_chunks:
        score = chunk.get("score", chunk.get("fusion_score", 0.0))
        code = chunk.get(code_key, "")
        snippet = f"# Retrieved (score={score:.3f}):\n{code}\n"
        if total + len(snippet) > max_chars and parts:
            break
        parts.append(snippet)
        total += len(snippet)
    return "\n".join(parts)


def build_augmented_prompt(query: str, retrieved_context: str, task_instruction: str = "") -> str:
    """Combine retrieved context with the original query into the final
    RAG-augmented prompt handed to the generation model (small LM or LLM)."""
    sections = []
    if retrieved_context:
        sections.append(retrieved_context)
    if task_instruction:
        sections.append(task_instruction)
    sections.append(query)
    return "\n".join(sections)


def dynamic_top_k(
    scored_results: list[dict[str, Any]],
    score_key: str = "score",
    min_k: int = 1,
    max_k: int = 10,
    score_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    """Adaptive Top-K: include every result scoring at/above ``score_threshold``,
    bounded to ``[min_k, max_k]``. Falls back to the top ``min_k`` results if
    nothing clears the threshold, so a query never comes back empty-handed.
    """
    sorted_results = sorted(scored_results, key=lambda r: r.get(score_key, 0.0), reverse=True)
    above_threshold = [r for r in sorted_results if r.get(score_key, 0.0) >= score_threshold]

    if len(above_threshold) < min_k:
        return sorted_results[:min_k]
    return above_threshold[:max_k]
