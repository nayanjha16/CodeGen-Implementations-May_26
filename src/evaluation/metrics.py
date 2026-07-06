"""Evaluation metrics for SQL generation."""

from __future__ import annotations

from typing import Any

import sqlparse

from src.evaluation.structural_similarity import sql_structural_similarity_batch


class EvaluationMetrics:
    """Compute execution, exact match, and structural metrics for text-to-SQL."""

    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for exact match comparison."""
        sql = sql.strip().rstrip(";")
        try:
            return sqlparse.format(sql, reindent=True, keyword_case="upper")
        except Exception:
            return sql.upper().strip()

    def exact_match(self, predicted: str, reference: str) -> bool:
        """Exact match accuracy after normalization."""
        return self.normalize_sql(predicted) == self.normalize_sql(reference)

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

    def execution_accuracy(
        self,
        predictions: list[str],
        references: list[str],
        execution_contexts: list[dict[str, str] | None],
    ) -> float:
        """Execution accuracy comparing predicted SQL against gold or live reference output."""
        from src.evaluation.database_execution import _ExecutionSession, is_database_available
        from src.evaluation.gold_output_comparison import compare_predicted_sql_to_gold_output

        if not is_database_available():
            return 0.0

        correct = 0
        total = 0

        try:
            with _ExecutionSession() as session:
                for pred, ref, context in zip(
                    predictions, references, execution_contexts
                ):
                    if not context:
                        continue
                    db_id = context.get("db_id", "").strip()
                    dataset = context.get("dataset", "spider").strip() or "spider"
                    if not db_id:
                        continue
                    total += 1
                    gold_sql_output = str(context.get("sql_output", "")).strip()
                    if gold_sql_output:
                        result = compare_predicted_sql_to_gold_output(
                            pred,
                            gold_sql_output,
                            reference_sql=ref,
                            db_id=db_id,
                            dataset=dataset,
                            session=session,
                        )
                    else:
                        result = session.compare_sql(
                            dataset=dataset,
                            db_id=db_id,
                            predicted_sql=pred,
                            reference_sql=ref,
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
        execution_contexts: list[dict[str, str] | None] | None = None,
    ) -> dict[str, Any]:
        """Run the text-to-SQL evaluation suite."""
        metrics = {
            "execution_accuracy": self.execution_accuracy(
                predictions,
                references,
                execution_contexts or [None] * len(predictions),
            ),
            "exact_match": self.exact_match_batch(predictions, references),
            "structural_similarity": sql_structural_similarity_batch(
                predictions, references
            ),
        }
        return metrics
