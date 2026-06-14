"""Export per-sample evaluation details for manual review."""

from __future__ import annotations

import csv
from pathlib import Path

from src.evaluation.metrics import EvaluationMetrics

METRICS_JSON = "metrics.json"
TEXT2SQL_DETAILS_CSV = "text2sql_details.csv"
SQL2NOSQL_DETAILS_CSV = "sql2nosql_details.csv"


def save_text2sql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    metrics: EvaluationMetrics | None = None,
    db_paths: list[str | None] | None = None,
) -> Path:
    """Write text-to-SQL per-sample details to CSV."""
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


def save_sql2nosql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
) -> Path:
    """Write SQL-to-MongoDB per-sample details to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    from src.sql2nosql.evaluator import NoSQLEvaluator

    evaluator = NoSQLEvaluator()

    fieldnames = [
        "index",
        "question",
        "db_id",
        "predicted_sql",
        "reference_sql",
        "predicted_sql_valid",
        "reference_sql_valid",
        "predicted_mongodb_query",
        "reference_mongodb_query",
        "reference_translation_success",
        "mongodb_warnings",
        "mongodb_success",
        "exact_match",
        "syntax_valid",
        "structural_match",
        "token_f1",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, pred in enumerate(predictions):
            predicted_sql = pred.get("sql", "")
            reference_sql = pred.get("reference_sql", pred.get("ground_truth", ""))
            predicted_mongodb = pred.get("predicted_mongodb_query", "")
            reference_mongodb = pred.get("reference_mongodb_query", "")

            structural_match = ""
            exact_match = ""
            syntax_valid = ""
            token_f1 = ""

            if predicted_mongodb and reference_mongodb:
                accuracy = evaluator.translation_accuracy(
                    predicted_mongodb, reference_mongodb
                )
                exact_match = accuracy["exact_match"]
                token_f1 = accuracy["token_f1"]
                syntax_valid = evaluator.validate_syntax(predicted_mongodb)["valid"]
                structural_match = evaluator.query_equivalence(
                    {
                        "collection": pred.get("collection", ""),
                        "filter": pred.get("filter", {}),
                        "projection": pred.get("projection", {}),
                    },
                    {
                        "collection": pred.get("reference_collection", ""),
                        "filter": pred.get("reference_filter", {}),
                        "projection": pred.get("reference_projection", {}),
                    },
                )["equivalent"]

            writer.writerow(
                {
                    "index": idx,
                    "question": pred.get("question", ""),
                    "db_id": pred.get("db_id", ""),
                    "predicted_sql": predicted_sql,
                    "reference_sql": reference_sql,
                    "predicted_sql_valid": pred.get("predicted_sql_valid", ""),
                    "reference_sql_valid": pred.get("reference_sql_valid", ""),
                    "predicted_mongodb_query": predicted_mongodb,
                    "reference_mongodb_query": reference_mongodb,
                    "reference_translation_success": pred.get(
                        "reference_translation_success", ""
                    ),
                    "mongodb_warnings": pred.get("mongodb_warnings", ""),
                    "mongodb_success": pred.get("mongodb_success", ""),
                    "exact_match": exact_match,
                    "syntax_valid": syntax_valid,
                    "structural_match": structural_match,
                    "token_f1": token_f1,
                }
            )

    return output_path
