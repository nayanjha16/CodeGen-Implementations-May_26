"""NoSQL translation evaluation module."""

from __future__ import annotations

import re
from typing import Any


class NoSQLEvaluator:
    """Evaluate SQL to MongoDB translation quality."""

    def normalize_query(self, query: str) -> str:
        """Normalize MongoDB query for comparison."""
        q = query.strip()
        q = re.sub(r"\s+", " ", q)
        q = q.replace("\n", " ")
        q = re.sub(r"\s*,\s*", ", ", q)
        return q.lower()

    def translation_accuracy(
        self,
        predicted: str,
        reference: str,
    ) -> dict[str, Any]:
        """Compare predicted vs reference MongoDB query."""
        pred_norm = self.normalize_query(predicted)
        ref_norm = self.normalize_query(reference)
        exact_match = pred_norm == ref_norm

        pred_tokens = set(re.findall(r"\w+", pred_norm))
        ref_tokens = set(re.findall(r"\w+", ref_norm))
        overlap = len(pred_tokens & ref_tokens)
        union = len(pred_tokens | ref_tokens) or 1
        token_f1 = 2 * overlap / (len(pred_tokens) + len(ref_tokens)) if pred_tokens or ref_tokens else 0.0

        return {
            "exact_match": exact_match,
            "token_overlap": overlap / union,
            "token_f1": token_f1,
        }

    def query_equivalence(
        self,
        predicted: dict[str, Any],
        reference: dict[str, Any],
    ) -> dict[str, Any]:
        """Check structural equivalence of parsed query components."""
        pred_filter = predicted.get("filter", {})
        ref_filter = reference.get("filter", {})
        pred_proj = predicted.get("projection", {})
        ref_proj = reference.get("projection", {})

        filter_match = pred_filter == ref_filter
        projection_match = pred_proj == ref_proj
        collection_match = predicted.get("collection") == reference.get("collection")

        return {
            "equivalent": filter_match and projection_match and collection_match,
            "filter_match": filter_match,
            "projection_match": projection_match,
            "collection_match": collection_match,
        }

    def evaluate_batch(
        self,
        predictions: list[dict[str, str]],
        references: list[dict[str, str]],
    ) -> dict[str, float]:
        """Evaluate a batch of translations."""
        if not predictions:
            return {"translation_accuracy": 0.0, "exact_match_rate": 0.0}

        exact_matches = 0
        token_f1_scores = []

        for pred, ref in zip(predictions, references):
            result = self.translation_accuracy(
                pred.get("mongodb_query", ""),
                ref.get("mongodb_query", ""),
            )
            if result["exact_match"]:
                exact_matches += 1
            token_f1_scores.append(result["token_f1"])

        n = len(predictions)
        return {
            "translation_accuracy": sum(token_f1_scores) / n,
            "exact_match_rate": exact_matches / n,
            "count": n,
        }
