"""Export per-sample evaluation details for manual review."""

from __future__ import annotations

import csv
from pathlib import Path

from src.evaluation.metrics import EvaluationMetrics

METRICS_JSON = "metrics.json"
DETAILS_CSV = "details.csv"


def save_evaluation_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    metrics: EvaluationMetrics | None = None,
    db_paths: list[str | None] | None = None,
) -> Path:
    """Write prompt, model output, and per-sample metrics to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    evaluator = metrics or EvaluationMetrics()
    db_paths = db_paths or [None] * len(predictions)

    from src.text2sql.sql_validator import SQLValidator

    validator = SQLValidator()
    executor = None

    fieldnames = [
        "index",
        "question",
        "schema",
        "db_id",
        "db_path",
        "prompt",
        "raw_output",
        "predicted_sql",
        "ground_truth",
        "exact_match",
        "syntax_valid",
        "execution_match",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (pred, db_path) in enumerate(zip(predictions, db_paths)):
            predicted_sql = pred.get("sql", "")
            ground_truth = pred.get("ground_truth", "")
            execution_match = ""

            if db_path:
                if executor is None:
                    from src.text2sql.sql_executor import SQLExecutor

                    executor = SQLExecutor()
                result = executor.compare_results(
                    predicted_sql, ground_truth, db_path
                )
                execution_match = result.get("execution_match", False)

            writer.writerow(
                {
                    "index": idx,
                    "question": pred.get("question", ""),
                    "schema": pred.get("schema", ""),
                    "db_id": pred.get("db_id", ""),
                    "db_path": db_path or "",
                    "prompt": pred.get("prompt", ""),
                    "raw_output": pred.get("raw_output", ""),
                    "predicted_sql": predicted_sql,
                    "ground_truth": ground_truth,
                    "exact_match": evaluator.exact_match(predicted_sql, ground_truth),
                    "syntax_valid": validator.validate_syntax(predicted_sql)["valid"],
                    "execution_match": execution_match,
                }
            )

    return output_path
