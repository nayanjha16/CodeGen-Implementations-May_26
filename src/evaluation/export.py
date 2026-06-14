"""Export per-sample evaluation details for manual review."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from src.evaluation.qwen_evaluator import QwenEvaluator

METRICS_JSON = "metrics.json"
TEXT2SQL_DETAILS_CSV = "text2sql_details.csv"
SQL2NOSQL_DETAILS_CSV = "sql2nosql_details.csv"

TEXT2SQL_DETAIL_FIELDS = [
    "index",
    "question",
    "prompt",
    "raw_output",
    "predicted_sql",
    "predicted_sql_valid",
    "ground_truth",
    "qwen_sql_correct",
    "qwen_raw_response",
]

SQL2NOSQL_DETAIL_FIELDS = [
    "question",
    "schema",
    "reference_sql",
    "nosql_schema",
    "predicted_mongodb_query",
    "reference_mongodb_query",
    "mongodb_warnings",
    "mongodb_success",
    "qwen_query_correct",
    "qwen_raw_response",
]


def _derive_nosql_schema(schema: str) -> str:
    """Best-effort MongoDB schema from SQL schema text when available."""
    if not schema.strip():
        return ""
    try:
        from TEND.sql_schema_to_mongo_schema import convert_schema_json

        return convert_schema_json(schema)
    except Exception:
        return ""


def save_text2sql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    db_paths: list[str | None] | None = None,
    qwen_evaluator: QwenEvaluator | None = None,
    use_qwen: bool = True,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write text-to-SQL per-sample details to CSV using Qwen semantic evaluation."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    db_paths = db_paths or [None] * len(predictions)
    evaluator = qwen_evaluator
    if use_qwen and evaluator is None:
        evaluator = QwenEvaluator()

    fieldnames = TEXT2SQL_DETAIL_FIELDS

    qwen_results: list[dict[str, Any]] = []
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (pred, _db_path) in enumerate(zip(predictions, db_paths)):
            predicted_sql = pred.get("sql", "")
            ground_truth = pred.get("ground_truth", "")
            predicted_sql_valid = pred.get("sql_valid", "")

            qwen_eval: dict[str, Any] = {}
            if use_qwen and evaluator is not None:
                sql_valid = (
                    predicted_sql_valid
                    if isinstance(predicted_sql_valid, bool)
                    else None
                )
                qwen_eval = evaluator.evaluate_text2sql_sample(
                    question=pred.get("question", ""),
                    schema=pred.get("schema", ""),
                    predicted_sql=predicted_sql,
                    ground_truth_sql=ground_truth,
                    raw_output=pred.get("raw_output", ""),
                    prompt=pred.get("prompt", ""),
                    predicted_sql_valid=sql_valid,
                )
                qwen_results.append(qwen_eval)
                if predicted_sql_valid == "":
                    predicted_sql_valid = qwen_eval.get("predicted_sql_valid", "")

            writer.writerow(
                {
                    "index": idx,
                    "question": pred.get("question", ""),
                    "prompt": pred.get("prompt", ""),
                    "raw_output": pred.get("raw_output", ""),
                    "predicted_sql": predicted_sql,
                    "predicted_sql_valid": predicted_sql_valid,
                    "ground_truth": ground_truth,
                    "qwen_sql_correct": qwen_eval.get("sql_correct", ""),
                    "qwen_raw_response": qwen_eval.get("raw_response", ""),
                }
            )

    summary = (
        QwenEvaluator.summarize_text2sql(qwen_results)
        if use_qwen
        else {"sql_correct_rate": 0.0, "count": len(predictions)}
    )
    return output_path, qwen_results, summary


def save_sql2nosql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    qwen_evaluator: QwenEvaluator | None = None,
    use_qwen: bool = True,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write SQL-to-MongoDB per-sample details to CSV using Qwen semantic evaluation."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    evaluator = qwen_evaluator
    if use_qwen and evaluator is None:
        evaluator = QwenEvaluator()

    fieldnames = SQL2NOSQL_DETAIL_FIELDS

    qwen_results: list[dict[str, Any]] = []
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for pred in predictions:
            reference_sql = pred.get("reference_sql", pred.get("ground_truth", ""))
            predicted_mongodb = pred.get("predicted_mongodb_query", "")
            reference_mongodb = pred.get("reference_mongodb_query", "")
            schema = pred.get("schema", "")
            nosql_schema = pred.get("nosql_schema", "") or _derive_nosql_schema(schema)

            qwen_eval: dict[str, Any] = {}
            if use_qwen and evaluator is not None:
                qwen_eval = evaluator.evaluate_sql2nosql_sample(
                    predicted_mongodb_query=predicted_mongodb,
                    reference_mongodb_query=reference_mongodb,
                )
                qwen_results.append(qwen_eval)

            writer.writerow(
                {
                    "question": pred.get("question", ""),
                    "schema": schema,
                    "reference_sql": reference_sql,
                    "nosql_schema": nosql_schema,
                    "predicted_mongodb_query": predicted_mongodb,
                    "reference_mongodb_query": reference_mongodb,
                    "mongodb_warnings": pred.get("mongodb_warnings", ""),
                    "mongodb_success": pred.get("mongodb_success", ""),
                    "qwen_query_correct": qwen_eval.get("query_correct", ""),
                    "qwen_raw_response": qwen_eval.get("raw_response", ""),
                }
            )

    summary = (
        QwenEvaluator.summarize_sql2nosql(qwen_results)
        if use_qwen
        else {
            "query_correct_rate": 0.0,
            "overall_correct_rate": 0.0,
            "count": len(predictions),
        }
    )
    return output_path, qwen_results, summary
