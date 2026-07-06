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
            re.match(
                r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
                q,
                re.IGNORECASE,
            )
        )
        return {"valid": valid}

    def execution_accuracy(
        self,
        predicted_queries: list[str],
        reference_sql_queries: list[str],
        execution_contexts: list[dict[str, str] | None],
    ) -> float:
        """Compare predicted MongoDB output against reference SQL on live databases."""
        from src.evaluation.database_execution import _ExecutionSession, is_database_available

        if not is_database_available():
            return 0.0

        correct = 0
        total = 0

        try:
            with _ExecutionSession() as session:
                for pred, ref_sql, context in zip(
                    predicted_queries,
                    reference_sql_queries,
                    execution_contexts,
                ):
                    if not context:
                        continue
                    db_id = context.get("db_id", "").strip()
                    dataset = context.get("dataset", "spider").strip() or "spider"
                    if not db_id or not ref_sql.strip() or not pred.strip():
                        continue
                    total += 1
                    result = session.compare_sql_to_mongo(
                        dataset=dataset,
                        db_id=db_id,
                        reference_sql=ref_sql,
                        predicted_mongo=pred,
                    )
                    if result.match:
                        correct += 1
        except RuntimeError:
            return 0.0

        return correct / total if total > 0 else 0.0

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        reference_sql_queries: list[str] | None = None,
        execution_contexts: list[dict[str, str] | None] | None = None,
    ) -> dict[str, Any]:
        """Run full evaluation suite for MongoDB query translation."""
        from src.evaluation.structural_similarity import mongo_structural_similarity_batch

        ref_sql = reference_sql_queries or [""] * len(predictions)
        contexts = execution_contexts or [None] * len(predictions)
        return {
            "execution_accuracy": self.execution_accuracy(
                predictions, ref_sql, contexts
            ),
            "exact_match": self.exact_match_batch(predictions, references),
            "structural_similarity": mongo_structural_similarity_batch(
                predictions, references
            ),
        }

    def evaluate_batch(
        self,
        predictions: list[dict[str, str]],
        references: list[dict[str, str]],
    ) -> dict[str, float]:
        """Evaluate a batch of translations."""
        if not predictions:
            return {
                "execution_accuracy": 0.0,
                "exact_match": 0.0,
                "structural_similarity": 0.0,
            }

        pred_queries = [p.get("mongodb_query", "") for p in predictions]
        ref_queries = [r.get("mongodb_query", "") for r in references]
        ref_sql = [p.get("reference_sql", "") for p in predictions]
        contexts = [
            {"db_id": p.get("db_id", ""), "dataset": p.get("source_dataset", "spider")}
            for p in predictions
        ]
        return self.evaluate_all(
            pred_queries,
            ref_queries,
            reference_sql_queries=ref_sql,
            execution_contexts=contexts,
        )
