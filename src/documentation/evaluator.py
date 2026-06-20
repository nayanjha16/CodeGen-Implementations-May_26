"""Documentation generation evaluation module."""

from __future__ import annotations

import re
from typing import Any

from src.documentation.reference_builder import ReferenceDocumentationBuilder


class DocumentationEvaluator:
    """Evaluate MongoDB query documentation quality."""

    def __init__(self, reference_builder: ReferenceDocumentationBuilder | None = None):
        self.reference_builder = reference_builder or ReferenceDocumentationBuilder()

    def normalize_documentation(self, text: str) -> str:
        """Normalize documentation for comparison."""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"^```(?:markdown|text)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
        return text.lower()

    def exact_match(self, predicted: str, reference: str) -> bool:
        """Exact match after documentation normalization."""
        return self.normalize_documentation(predicted) == self.normalize_documentation(
            reference
        )

    def exact_match_batch(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Batch exact match accuracy."""
        if not predictions:
            return 0.0
        matches = sum(
            1 for pred, ref in zip(predictions, references) if self.exact_match(pred, ref)
        )
        return matches / len(predictions)

    def validate_structure(
        self,
        documentation: str,
        mongodb_query: str = "",
    ) -> dict[str, Any]:
        """Check whether generated documentation looks usable."""
        text = documentation.strip()
        if len(text) < 20:
            return {"valid": False, "reason": "Documentation is too short"}

        if re.search(r"db\.\w+\.(find|aggregate|distinct|countDocuments)\s*\(", text):
            return {"valid": False, "reason": "Documentation contains raw MongoDB code"}

        structured = self.reference_builder.to_structured(mongodb_query)
        if structured.get("valid"):
            collection = structured["collection"].lower()
            if collection and collection not in text.lower():
                return {
                    "valid": False,
                    "reason": f"Documentation does not mention collection `{structured['collection']}`",
                }

        return {"valid": True, "reason": ""}

    def syntax_validity_rate(
        self,
        predictions: list[str],
        mongodb_queries: list[str] | None = None,
    ) -> float:
        """Fraction of structurally valid documentation predictions."""
        if not predictions:
            return 0.0
        queries = mongodb_queries or [""] * len(predictions)
        valid = sum(
            1
            for doc, query in zip(predictions, queries)
            if self.validate_structure(doc, query)["valid"]
        )
        return valid / len(predictions)

    def structural_equivalence_rate(
        self,
        structured_preds: list[dict[str, Any]],
        structured_refs: list[dict[str, Any]],
    ) -> float:
        """Fraction of docs whose parsed collection/operation metadata matches."""
        if not structured_preds:
            return 0.0
        matches = sum(
            1
            for pred, ref in zip(structured_preds, structured_refs)
            if pred.get("collection") == ref.get("collection")
            and pred.get("operation") == ref.get("operation")
        )
        return matches / len(structured_preds)

    def token_f1_batch(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Average token F1 across documentation predictions."""
        if not predictions:
            return 0.0
        scores = [
            self.documentation_accuracy(pred, ref)["token_f1"]
            for pred, ref in zip(predictions, references)
        ]
        return sum(scores) / len(scores)

    def documentation_accuracy(
        self,
        predicted: str,
        reference: str,
    ) -> dict[str, Any]:
        """Compare predicted vs reference documentation."""
        pred_norm = self.normalize_documentation(predicted)
        ref_norm = self.normalize_documentation(reference)
        exact_match = pred_norm == ref_norm

        pred_tokens = set(re.findall(r"\w+", pred_norm))
        ref_tokens = set(re.findall(r"\w+", ref_norm))
        overlap = len(pred_tokens & ref_tokens)
        token_f1 = (
            2 * overlap / (len(pred_tokens) + len(ref_tokens))
            if pred_tokens or ref_tokens
            else 0.0
        )

        return {
            "exact_match": exact_match,
            "token_overlap": overlap / (len(pred_tokens | ref_tokens) or 1),
            "token_f1": token_f1,
        }

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        mongodb_queries: list[str] | None = None,
        structured_preds: list[dict[str, Any]] | None = None,
        structured_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run full evaluation suite for MongoDB query documentation."""
        from src.evaluation.metrics import EvaluationMetrics

        text_metrics = EvaluationMetrics()
        codebleu = text_metrics.compute_codebleu(predictions, references, lang="python")
        metrics: dict[str, Any] = {
            "exact_match": self.exact_match_batch(predictions, references),
            "syntax_validity": self.syntax_validity_rate(
                predictions, mongodb_queries=mongodb_queries
            ),
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
