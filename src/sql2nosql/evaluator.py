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

    def exact_match(self, predicted: str, reference: str) -> bool:
        """Exact match after MongoDB query normalization."""
        return self.normalize_query(predicted) == self.normalize_query(reference)

    def exact_match_batch(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Batch exact match accuracy."""
        if not predictions:
            return 0.0
        matches = sum(
            1 for p, r in zip(predictions, references) if self.exact_match(p, r)
        )
        return matches / len(predictions)

    def validate_syntax(self, query: str) -> dict[str, Any]:
        """Check whether a string looks like valid MongoDB shell syntax."""
        q = query.strip()
        valid = bool(
            re.match(r"db\.\w+\.(find|aggregate|distinct)\s*\(", q)
        )
        return {"valid": valid}

    def syntax_validity_rate(self, predictions: list[str]) -> float:
        """Fraction of syntactically valid MongoDB query predictions."""
        if not predictions:
            return 0.0
        valid = sum(1 for p in predictions if self.validate_syntax(p)["valid"])
        return valid / len(predictions)

    def structural_equivalence_rate(
        self,
        structured_preds: list[dict[str, Any]],
        structured_refs: list[dict[str, Any]],
    ) -> float:
        """Fraction of structurally equivalent filter/projection/collection."""
        if not structured_preds:
            return 0.0
        matches = sum(
            1
            for pred, ref in zip(structured_preds, structured_refs)
            if self.query_equivalence(pred, ref)["equivalent"]
        )
        return matches / len(structured_preds)

    def token_f1_batch(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Average token F1 across predictions."""
        if not predictions:
            return 0.0
        scores = [
            self.translation_accuracy(p, r)["token_f1"]
            for p, r in zip(predictions, references)
        ]
        return sum(scores) / len(scores)

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
        token_f1 = (
            2 * overlap / (len(pred_tokens) + len(ref_tokens))
            if pred_tokens or ref_tokens
            else 0.0
        )

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

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        structured_preds: list[dict[str, Any]] | None = None,
        structured_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run full evaluation suite for MongoDB query translation."""
        from src.evaluation.metrics import EvaluationMetrics

        text_metrics = EvaluationMetrics()
        codebleu = text_metrics.compute_codebleu(
            predictions, references, lang="javascript"
        )
        metrics: dict[str, Any] = {
            "exact_match": self.exact_match_batch(predictions, references),
            "syntax_validity": self.syntax_validity_rate(predictions),
            "token_f1": self.token_f1_batch(predictions, references),
            "bleu": text_metrics.compute_bleu(predictions, references),
            "rouge_l": text_metrics.compute_rouge_l(predictions, references),
            "bertscore": text_metrics.compute_bertscore(predictions, references),
            **codebleu,
            "count": len(predictions),
        }

        if structured_preds and structured_refs:
            metrics["structural_equivalence"] = self.structural_equivalence_rate(
                structured_preds, structured_refs
            )

        return metrics

    def evaluate_batch(
        self,
        predictions: list[dict[str, str]],
        references: list[dict[str, str]],
    ) -> dict[str, float]:
        """Evaluate a batch of translations."""
        if not predictions:
            return {
                "exact_match": 0.0,
                "syntax_validity": 0.0,
                "token_f1": 0.0,
                "count": 0,
            }

        pred_queries = [p.get("mongodb_query", "") for p in predictions]
        ref_queries = [r.get("mongodb_query", "") for r in references]
        return self.evaluate_all(pred_queries, ref_queries, predictions, references)
