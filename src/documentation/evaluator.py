"""Documentation generation evaluation module."""

from __future__ import annotations

import re
from typing import Any

from src.evaluation.embedding_similarity import embedding_similarity_batch
from src.utils.config import get_embedding_model_name


class DocumentationEvaluator:
    """Evaluate MongoDB query documentation quality."""

    def normalize_documentation(self, text: str) -> str:
        """Normalize documentation text for exact match comparison."""
        normalized = text.strip()
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.casefold()

    def exact_match(self, predicted: str, reference: str) -> bool:
        """Exact match after whitespace and case normalization."""
        return self.normalize_documentation(predicted) == self.normalize_documentation(
            reference
        )

    def exact_match_batch(
        self,
        predictions: list[str],
        references: list[str],
    ) -> float:
        """Batch exact match accuracy."""
        if not predictions:
            return 0.0
        matches = sum(
            1 for pred, ref in zip(predictions, references) if self.exact_match(pred, ref)
        )
        return matches / len(predictions)

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        *,
        embedding_model: str | None = None,
    ) -> dict[str, Any]:
        """Run documentation evaluation using exact match and embedding similarity."""
        model_name = embedding_model or get_embedding_model_name()
        return {
            "exact_match": self.exact_match_batch(predictions, references),
            "embedding_similarity": embedding_similarity_batch(
                predictions,
                references,
                model_name=model_name,
            ),
        }
