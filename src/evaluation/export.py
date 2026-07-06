"""Export per-sample evaluation details for manual review."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

from src.evaluation.ollama_judge import OllamaJudge
from src.llm.factory import create_judge
from src.models.model_loader import count_input_tokens
from src.utils.config import get_model_name, load_config
from src.utils.logging import log_batch_progress, log_step

logger = logging.getLogger("codegen")

METRICS_JSON = "metrics.json"
TEXT2SQL_DETAILS_CSV = "text2sql_details.csv"
SQL2NOSQL_DETAILS_CSV = "sql2nosql_details.csv"
DOCUMENTATION_DETAILS_CSV = "documentation_details.csv"

TEXT2SQL_METRIC_KEYS = [
    "execution_accuracy",
    "exact_match",
    "structural_similarity",
]

SQL2NOSQL_METRIC_KEYS = [
    "execution_accuracy",
    "exact_match",
    "structural_similarity",
]

DOCUMENTATION_METRIC_KEYS = [
    "exact_match",
    "embedding_similarity",
    "judge_score",
]


def merge_judge_summary_into_metrics(
    base_metrics: dict[str, Any] | None,
    judge_summary: dict[str, Any] | None,
    *,
    task: str,
) -> dict[str, Any]:
    """Merge documentation judge scores into metrics."""
    merged = dict(base_metrics or {})
    if judge_summary and task == "documentation":
        merged["judge_score"] = judge_summary.get("judge_score", 0.0)
    return normalize_task_metrics(merged, task=task)


def normalize_task_metrics(
    metrics: dict[str, Any] | None,
    *,
    task: str,
) -> dict[str, Any]:
    """Return metrics with the canonical keys for each task."""
    source = dict(metrics or {})
    if task == "text2sql":
        keys = TEXT2SQL_METRIC_KEYS
    elif task == "sql2nosql":
        keys = SQL2NOSQL_METRIC_KEYS
    else:
        keys = DOCUMENTATION_METRIC_KEYS

    normalized: dict[str, Any] = {}
    for key in keys:
        normalized[key] = source.get(key, 0.0)
    return normalized


TEXT2SQL_DETAIL_FIELDS = [
    "index",
    "question",
    "prompt",
    "input_token_count",
    "raw_output",
    "predicted_sql",
    "predicted_sql_valid",
    "ground_truth",
    "exact_match",
    "execution_match",
    "execution_error",
]

SQL2NOSQL_DETAIL_FIELDS = [
    "reference_sql",
    "prompt",
    "input_token_count",
    "raw_output",
    "predicted_mongodb_query",
    "reference_mongodb_query",
    "mongodb_warnings",
    "mongodb_success",
    "exact_match",
    "structural_similarity",
    "execution_match",
    "gold_sql_output_match",
    "execution_error",
]

DOCUMENTATION_DETAIL_FIELDS = [
    "mongodb_query",
    "prompt",
    "input_token_count",
    "raw_output",
    "predicted_documentation",
    "reference_documentation",
    "exact_match",
    "judge_score",
    "judge_correctness",
    "judge_completeness",
    "judge_clarity",
    "judge_relevance",
    "judge_reason",
    "judge_raw_response",
]


def _execution_context_from_prediction(pred: dict[str, str]) -> dict[str, str] | None:
    db_id = str(pred.get("db_id", "")).strip()
    if not db_id:
        return None
    dataset = str(pred.get("source_dataset", "spider")).strip() or "spider"
    return {"db_id": db_id, "dataset": dataset}


def save_text2sql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
) -> tuple[Path, list[dict[str, Any]]]:
    """Write text-to-SQL per-sample details to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("text2sql", "Exporting details CSV (%d rows)", total)

    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)
    from src.evaluation.database_execution import compare_sql_execution, is_database_available
    from src.evaluation.gold_output_comparison import compare_predicted_sql_to_gold_output
    from src.evaluation.metrics import EvaluationMetrics

    db_available = is_database_available()
    sql_metrics = EvaluationMetrics()
    detail_rows: list[dict[str, Any]] = []

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TEXT2SQL_DETAIL_FIELDS)
        writer.writeheader()

        for idx, pred in enumerate(predictions):
            log_batch_progress("text2sql", idx + 1, total, every=25)
            predicted_sql = pred.get("sql", "")
            ground_truth = pred.get("ground_truth", "")
            predicted_sql_valid = pred.get("sql_valid", "")
            prompt = pred.get("prompt", "")
            input_token_count = pred.get("input_token_count")
            if input_token_count in ("", None):
                input_token_count = count_input_tokens(
                    prompt,
                    model_name=generation_model,
                    config=cfg,
                )

            execution_match = ""
            execution_error = ""
            exact_match = ""
            if predicted_sql and ground_truth:
                exact_match = sql_metrics.exact_match(predicted_sql, ground_truth)
            if db_available:
                context = _execution_context_from_prediction(pred)
                gold_sql_output = str(pred.get("sql_output", "")).strip()
                if context and predicted_sql:
                    if gold_sql_output:
                        comparison = compare_predicted_sql_to_gold_output(
                            predicted_sql,
                            gold_sql_output,
                            reference_sql=ground_truth,
                            db_id=context["db_id"],
                            dataset=context["dataset"],
                        )
                    elif ground_truth:
                        comparison = compare_sql_execution(
                            predicted_sql,
                            ground_truth,
                            db_id=context["db_id"],
                            dataset=context["dataset"],
                        )
                    else:
                        comparison = None
                    if comparison is not None:
                        execution_match = comparison.match
                        execution_error = comparison.error or comparison.diff_summary or ""

            row = {
                "index": idx,
                "question": pred.get("question", ""),
                "prompt": prompt,
                "input_token_count": input_token_count,
                "raw_output": pred.get("raw_output", ""),
                "predicted_sql": predicted_sql,
                "predicted_sql_valid": predicted_sql_valid,
                "ground_truth": ground_truth,
                "exact_match": exact_match,
                "execution_match": execution_match,
                "execution_error": execution_error,
            }
            detail_rows.append(row)
            writer.writerow(row)

    logger.info("[%s] Details CSV saved: %s", "text2sql (Text-to-SQL)", output_path)
    return output_path, detail_rows


def save_sql2nosql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
) -> tuple[Path, list[dict[str, Any]]]:
    """Write SQL-to-MongoDB per-sample details to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("sql2nosql", "Exporting details CSV (%d rows)", total)

    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)
    from src.evaluation.database_execution import compare_sql_to_mongo_execution, is_database_available
    from src.evaluation.gold_output_comparison import compare_predicted_mongo_to_gold_outputs
    from src.evaluation.structural_similarity import mongo_structural_similarity
    from src.sql2nosql.evaluator import NoSQLEvaluator

    db_available = is_database_available()
    nosql_evaluator = NoSQLEvaluator()
    detail_rows: list[dict[str, Any]] = []

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SQL2NOSQL_DETAIL_FIELDS)
        writer.writeheader()

        for idx, pred in enumerate(predictions):
            log_batch_progress("sql2nosql", idx + 1, total, every=25)
            reference_sql = pred.get("reference_sql", pred.get("ground_truth", ""))
            predicted_mongodb = pred.get("predicted_mongodb_query", "")
            reference_mongodb = pred.get("reference_mongodb_query", "")
            prompt = pred.get("nosql_prompt", pred.get("prompt", ""))
            input_token_count = pred.get("input_token_count")
            if input_token_count in ("", None):
                input_token_count = count_input_tokens(
                    prompt,
                    model_name=generation_model,
                    config=cfg,
                )

            execution_match = ""
            gold_sql_output_match = ""
            execution_error = ""
            exact_match = ""
            structural_similarity = ""
            if predicted_mongodb and reference_mongodb:
                exact_match = nosql_evaluator.exact_match(
                    predicted_mongodb,
                    reference_mongodb,
                )
                structural_similarity = mongo_structural_similarity(
                    predicted_mongodb,
                    reference_mongodb,
                )
            if db_available:
                context = _execution_context_from_prediction(pred)
                gold_nosql_output = str(
                    pred.get("gold_nosql_output", pred.get("nosql_output", ""))
                ).strip()
                gold_sql_output = str(
                    pred.get("gold_sql_output", pred.get("sql_output", ""))
                ).strip()
                if context and predicted_mongodb:
                    if gold_nosql_output:
                        comparison, sql_comparison = compare_predicted_mongo_to_gold_outputs(
                            predicted_mongodb,
                            gold_nosql_output,
                            gold_sql_output=gold_sql_output,
                            reference_sql=reference_sql,
                            reference_mongo_query=reference_mongodb,
                            db_id=context["db_id"],
                            dataset=context["dataset"],
                        )
                        execution_match = comparison.match
                        execution_error = comparison.error or comparison.diff_summary or ""
                        if sql_comparison is not None:
                            gold_sql_output_match = sql_comparison.match
                    elif reference_sql:
                        comparison = compare_sql_to_mongo_execution(
                            reference_sql,
                            predicted_mongodb,
                            db_id=context["db_id"],
                            dataset=context["dataset"],
                        )
                        execution_match = comparison.match
                        execution_error = comparison.error or comparison.diff_summary or ""

            row = {
                "reference_sql": reference_sql,
                "prompt": prompt,
                "input_token_count": input_token_count,
                "raw_output": pred.get("nosql_raw_output", pred.get("raw_output", "")),
                "predicted_mongodb_query": predicted_mongodb,
                "reference_mongodb_query": reference_mongodb,
                "mongodb_warnings": pred.get("mongodb_warnings", ""),
                "mongodb_success": pred.get("mongodb_success", ""),
                "exact_match": exact_match,
                "structural_similarity": structural_similarity,
                "execution_match": execution_match,
                "gold_sql_output_match": gold_sql_output_match,
                "execution_error": execution_error,
            }
            detail_rows.append(row)
            writer.writerow(row)

    logger.info("[%s] Details CSV saved: %s", "sql2nosql (SQL-to-MongoDB)", output_path)
    return output_path, detail_rows


def run_documentation_judge(
    predictions: list[dict[str, str]],
    judge: OllamaJudge | None = None,
    *,
    use_judge: bool = True,
    config: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the documentation LLM judge over all predictions."""
    total = len(predictions)
    log_step("nosql2doc", "Running documentation judge (%d rows, judge=%s)", total, use_judge)

    if not use_judge:
        return [], {"judge_score": 0.0, "count": total}

    evaluator = judge
    if evaluator is None:
        evaluator = create_judge(config or load_config())

    judge_results: list[dict[str, Any]] = []
    for idx, pred in enumerate(predictions):
        log_batch_progress("nosql2doc", idx + 1, total, every=25)
        mongodb_query = pred.get(
            "input_mongodb_query",
            pred.get(
                "reference_mongodb_query",
                pred.get("mongodb_query", pred.get("predicted_mongodb_query", "")),
            ),
        )
        judge_eval = evaluator.evaluate_documentation_sample(
            mongodb_query=mongodb_query,
            raw_output=pred.get("doc_raw_output", pred.get("raw_output", "")),
            reference_sql=pred.get("reference_sql", pred.get("ground_truth", "")),
            predicted_documentation=pred.get("predicted_documentation", ""),
            reference_documentation=pred.get("reference_documentation", ""),
        )
        judge_results.append(judge_eval)

    summary = OllamaJudge.summarize_documentation(judge_results)
    return judge_results, summary


def save_documentation_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    judge: OllamaJudge | None = None,
    use_judge: bool = True,
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
    judge_results: list[dict[str, Any]] | None = None,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write MongoDB documentation per-sample details to CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("nosql2doc", "Exporting details CSV (%d rows, judge=%s)", total, use_judge)

    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)
    from src.documentation.evaluator import DocumentationEvaluator

    doc_evaluator = DocumentationEvaluator()

    if use_judge and judge_results is None:
        judge_results, summary = run_documentation_judge(
            predictions,
            judge=judge,
            use_judge=True,
            config=cfg,
        )
    elif use_judge and judge_results is not None:
        summary = OllamaJudge.summarize_documentation(judge_results)
    else:
        judge_results = []
        summary = {"judge_score": 0.0, "count": len(predictions)}

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DOCUMENTATION_DETAIL_FIELDS)
        writer.writeheader()

        for idx, pred in enumerate(predictions):
            log_batch_progress("nosql2doc", idx + 1, total, every=25)
            mongodb_query = pred.get(
                "input_mongodb_query",
                pred.get(
                    "reference_mongodb_query",
                    pred.get("mongodb_query", pred.get("predicted_mongodb_query", "")),
                ),
            )
            predicted_doc = pred.get("predicted_documentation", "")
            reference_doc = pred.get("reference_documentation", "")
            prompt = pred.get("doc_prompt", pred.get("prompt", ""))
            input_token_count = pred.get("input_token_count")
            if input_token_count in ("", None):
                input_token_count = count_input_tokens(
                    prompt,
                    model_name=generation_model,
                    config=cfg,
                )

            judge_eval = judge_results[idx] if idx < len(judge_results) else {}
            exact_match = ""
            if predicted_doc and reference_doc:
                exact_match = doc_evaluator.exact_match(predicted_doc, reference_doc)

            writer.writerow(
                {
                    "mongodb_query": mongodb_query,
                    "prompt": prompt,
                    "input_token_count": input_token_count,
                    "raw_output": pred.get("doc_raw_output", pred.get("raw_output", "")),
                    "predicted_documentation": predicted_doc,
                    "reference_documentation": reference_doc,
                    "exact_match": exact_match,
                    "judge_score": judge_eval.get("judge_score", ""),
                    "judge_correctness": judge_eval.get("correctness", ""),
                    "judge_completeness": judge_eval.get("completeness", ""),
                    "judge_clarity": judge_eval.get("clarity", ""),
                    "judge_relevance": judge_eval.get("relevance", ""),
                    "judge_reason": judge_eval.get("reason", ""),
                    "judge_raw_response": judge_eval.get("raw_response", ""),
                }
            )

    logger.info("[%s] Details CSV saved: %s", "nosql2doc (NoSQL-to-Documentation)", output_path)
    return output_path, judge_results, summary
