"""Export per-sample evaluation details for manual review."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

from src.evaluation.ollama_judge import OllamaJudge
from src.models.model_loader import count_input_tokens
from src.utils.config import get_model_name, load_config
from src.utils.logging import log_batch_progress, log_step

logger = logging.getLogger("codegen")

METRICS_JSON = "metrics.json"
TEXT2SQL_DETAILS_CSV = "text2sql_details.csv"
SQL2NOSQL_DETAILS_CSV = "sql2nosql_details.csv"
DOCUMENTATION_DETAILS_CSV = "documentation_details.csv"

TASK_METRIC_KEYS = [
    "exact_match",
    "syntax_validity",
    "token_f1",
    "bleu",
    "rouge_l",
    "bertscore",
    "codebleu",
    "ngram_match",
    "syntax_match",
    "semantic_match",
    "count",
    "execution_accuracy",
    "structural_equivalence",
    "total_count",
    "scored_count",
    "translation_success_rate",
    "judge_correct_rate",
    "judge_overall_correct_rate",
    "judge_count",
]


def merge_judge_summary_into_metrics(
    base_metrics: dict[str, Any] | None,
    judge_summary: dict[str, Any] | None,
    *,
    task: str,
) -> dict[str, Any]:
    """Merge Ollama judge aggregate metrics and normalize to the shared task schema."""
    merged = dict(base_metrics or {})
    if judge_summary:
        if task == "text2sql":
            merged["judge_correct_rate"] = judge_summary.get("sql_correct_rate")
            merged["judge_overall_correct_rate"] = judge_summary.get("sql_correct_rate")
        elif task == "sql2nosql":
            merged["judge_correct_rate"] = judge_summary.get("query_correct_rate")
            merged["judge_overall_correct_rate"] = judge_summary.get(
                "overall_correct_rate"
            )
        elif task == "documentation":
            merged["judge_correct_rate"] = judge_summary.get("doc_correct_rate")
            merged["judge_overall_correct_rate"] = judge_summary.get(
                "overall_correct_rate"
            )
        if "count" in judge_summary:
            merged["judge_count"] = judge_summary["count"]
    return normalize_task_metrics(merged, task=task)


def normalize_task_metrics(
    metrics: dict[str, Any] | None,
    *,
    task: str,
) -> dict[str, Any]:
    """Return metrics with the same keys for text2sql and sql2nosql."""
    source = dict(metrics or {})
    count = source.get("count", 0)

    if task == "text2sql":
        source.setdefault("total_count", count)
        source.setdefault("scored_count", count)
        source.setdefault(
            "translation_success_rate", source.get("syntax_validity", 0.0)
        )
    elif task == "sql2nosql":
        source.setdefault("execution_accuracy", 0.0)
    elif task == "documentation":
        source.setdefault("execution_accuracy", 0.0)
        source.setdefault("structural_equivalence", 0.0)

    normalized: dict[str, Any] = {}
    for key in TASK_METRIC_KEYS:
        if key in source:
            normalized[key] = source[key]
        elif key.startswith("judge_"):
            normalized[key] = None
        else:
            normalized[key] = 0.0
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
    "judge_sql_correct",
    "judge_reason",
    "judge_raw_response",
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
    "judge_query_correct",
    "judge_reason",
    "judge_raw_response",
]

DOCUMENTATION_DETAIL_FIELDS = [
    "mongodb_query",
    "prompt",
    "input_token_count",
    "raw_output",
    "judge_doc_correct",
    "judge_reason",
    "judge_raw_response",
]


def save_text2sql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    db_paths: list[str | None] | None = None,
    judge: OllamaJudge | None = None,
    use_judge: bool = True,
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write text-to-SQL per-sample details to CSV using Ollama semantic evaluation."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("text2sql", "Exporting details CSV (%d rows, judge=%s)", total, use_judge)

    db_paths = db_paths or [None] * len(predictions)
    evaluator = judge
    if use_judge and evaluator is None:
        evaluator = OllamaJudge()

    fieldnames = TEXT2SQL_DETAIL_FIELDS
    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)

    judge_results: list[dict[str, Any]] = []
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, (pred, _db_path) in enumerate(zip(predictions, db_paths)):
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

            judge_eval: dict[str, Any] = {}
            if use_judge and evaluator is not None:
                sql_valid = (
                    predicted_sql_valid
                    if isinstance(predicted_sql_valid, bool)
                    else None
                )
                judge_eval = evaluator.evaluate_text2sql_sample(
                    question=pred.get("question", ""),
                    schema=pred.get("schema", ""),
                    predicted_sql=predicted_sql,
                    ground_truth_sql=ground_truth,
                    raw_output=pred.get("raw_output", ""),
                    prompt=pred.get("prompt", ""),
                    predicted_sql_valid=sql_valid,
                )
                judge_results.append(judge_eval)
                if predicted_sql_valid == "":
                    predicted_sql_valid = judge_eval.get("predicted_sql_valid", "")

            writer.writerow(
                {
                    "index": idx,
                    "question": pred.get("question", ""),
                    "prompt": prompt,
                    "input_token_count": input_token_count,
                    "raw_output": pred.get("raw_output", ""),
                    "predicted_sql": predicted_sql,
                    "predicted_sql_valid": predicted_sql_valid,
                    "ground_truth": ground_truth,
                    "judge_sql_correct": judge_eval.get("sql_correct", ""),
                    "judge_reason": judge_eval.get("reason", ""),
                    "judge_raw_response": judge_eval.get("raw_response", ""),
                }
            )

    summary = (
        OllamaJudge.summarize_text2sql(judge_results)
        if use_judge
        else {"sql_correct_rate": 0.0, "count": len(predictions)}
    )
    logger.info("[%s] Details CSV saved: %s", "text2sql (Text-to-SQL)", output_path)
    return output_path, judge_results, summary


def save_sql2nosql_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    judge: OllamaJudge | None = None,
    use_judge: bool = True,
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write SQL-to-MongoDB per-sample details to CSV using Ollama semantic evaluation."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("sql2nosql", "Exporting details CSV (%d rows, judge=%s)", total, use_judge)

    evaluator = judge
    if use_judge and evaluator is None:
        evaluator = OllamaJudge()

    fieldnames = SQL2NOSQL_DETAIL_FIELDS
    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)

    judge_results: list[dict[str, Any]] = []
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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

            judge_eval: dict[str, Any] = {}
            if use_judge and evaluator is not None:
                judge_eval = evaluator.evaluate_sql2nosql_sample(
                    predicted_mongodb_query=predicted_mongodb,
                    reference_mongodb_query=reference_mongodb,
                    reference_sql=reference_sql,
                )
                judge_results.append(judge_eval)

            writer.writerow(
                {
                    "reference_sql": reference_sql,
                    "prompt": prompt,
                    "input_token_count": input_token_count,
                    "raw_output": pred.get("nosql_raw_output", pred.get("raw_output", "")),
                    "predicted_mongodb_query": predicted_mongodb,
                    "reference_mongodb_query": reference_mongodb,
                    "mongodb_warnings": pred.get("mongodb_warnings", ""),
                    "mongodb_success": pred.get("mongodb_success", ""),
                    "judge_query_correct": judge_eval.get("query_correct", ""),
                    "judge_reason": judge_eval.get("reason", ""),
                    "judge_raw_response": judge_eval.get("raw_response", ""),
                }
            )

    summary = (
        OllamaJudge.summarize_sql2nosql(judge_results)
        if use_judge
        else {
            "query_correct_rate": 0.0,
            "overall_correct_rate": 0.0,
            "count": len(predictions),
        }
    )
    logger.info("[%s] Details CSV saved: %s", "sql2nosql (SQL-to-MongoDB)", output_path)
    return output_path, judge_results, summary


def save_documentation_details_csv(
    path: str | Path,
    predictions: list[dict[str, str]],
    judge: OllamaJudge | None = None,
    use_judge: bool = True,
    model_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    """Write MongoDB documentation per-sample details to CSV using Ollama evaluation."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    log_step("nosql2doc", "Exporting details CSV (%d rows, judge=%s)", total, use_judge)

    evaluator = judge
    if use_judge and evaluator is None:
        evaluator = OllamaJudge()

    fieldnames = DOCUMENTATION_DETAIL_FIELDS
    cfg = config or load_config()
    generation_model = model_name or get_model_name(cfg)

    judge_results: list[dict[str, Any]] = []
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
            prompt = pred.get("doc_prompt", pred.get("prompt", ""))
            input_token_count = pred.get("input_token_count")
            if input_token_count in ("", None):
                input_token_count = count_input_tokens(
                    prompt,
                    model_name=generation_model,
                    config=cfg,
                )

            judge_eval: dict[str, Any] = {}
            if use_judge and evaluator is not None:
                raw_output = pred.get("doc_raw_output", pred.get("raw_output", ""))
                judge_eval = evaluator.evaluate_documentation_sample(
                    mongodb_query=mongodb_query,
                    raw_output=raw_output,
                    reference_sql=pred.get("reference_sql", pred.get("ground_truth", "")),
                )
                judge_results.append(judge_eval)

            writer.writerow(
                {
                    "mongodb_query": mongodb_query,
                    "prompt": prompt,
                    "input_token_count": input_token_count,
                    "raw_output": pred.get("doc_raw_output", pred.get("raw_output", "")),
                    "judge_doc_correct": judge_eval.get("doc_correct", ""),
                    "judge_reason": judge_eval.get("reason", ""),
                    "judge_raw_response": judge_eval.get("raw_response", ""),
                }
            )

    summary = (
        OllamaJudge.summarize_documentation(judge_results)
        if use_judge
        else {
            "doc_correct_rate": 0.0,
            "overall_correct_rate": 0.0,
            "count": len(predictions),
        }
    )
    logger.info("[%s] Details CSV saved: %s", "nosql2doc (NoSQL-to-Documentation)", output_path)
    return output_path, judge_results, summary
