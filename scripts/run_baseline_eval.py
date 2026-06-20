"""
Baseline model evaluation.

Computes: Exact Match, Execution Accuracy, Syntax Validity,
          BLEU, ROUGE-L, BERTScore, CodeBLEU

Usage:
  python scripts/run_baseline_eval.py                    # 5 samples, built-in reference data (fast)
  python scripts/run_baseline_eval.py --dataset spider   # Spider validation split
  python scripts/run_baseline_eval.py --dataset bird     # BirdBench validation split
  python scripts/run_baseline_eval.py --max-samples 20   # limit samples
  python scripts/run_baseline_eval.py --mlflow           # log to MLflow
  python scripts/run_baseline_eval.py --dataset spider --output spider_baseline
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.benchmark import BenchmarkRunner
from src.evaluation.export import (
    DOCUMENTATION_DETAILS_CSV,
    METRICS_JSON,
    SQL2NOSQL_DETAILS_CSV,
    TEXT2SQL_DETAILS_CSV,
    merge_qwen_summary_into_metrics,
    normalize_task_metrics,
    save_documentation_details_csv,
    save_sql2nosql_details_csv,
    save_text2sql_details_csv,
)
from src.evaluation.qwen_evaluator import QwenEvaluator
from src.models.model_loader import is_model_cached
from src.text2sql.sql_executor import build_text2sql_prompt
from src.utils.config import (
    get_bertscore_model_name,
    get_model_name,
    get_qwen_evaluator_model_name,
    load_config,
)
from src.utils.paths import (
    get_bird_data_dir,
    get_model_cache_dir,
    get_spider_data_dir,
    is_bird_cached,
    is_spider_cached,
    resolve_results_run_dir,
)
from src.utils.seeds import set_seeds

# Small built-in reference set for quick baseline (no download required)
QUICK_REFERENCE = [
    {
        "question": "Show all students older than 20",
        "schema": "Table students(id, name, age)",
        "sql": "SELECT name, age FROM students WHERE age > 20",
        "db_id": "students",
    },
    {
        "question": "List all course names",
        "schema": "Table courses(id, name, credits)",
        "sql": "SELECT name FROM courses",
        "db_id": "students",
    },
    {
        "question": "How many students are there?",
        "schema": "Table students(id, name, age)",
        "sql": "SELECT COUNT(*) FROM students",
        "db_id": "students",
    },
]


def _compute_text2sql_translation_success_rate(
    predictions: list[dict[str, object]],
) -> float:
    """Rate of predictions that are complete SELECT ... FROM SQL statements."""
    if not predictions:
        return 0.0

    from src.text2sql.sql_validator import SQLValidator

    validator = SQLValidator()
    successful = 0

    for pred in predictions:
        sql_valid = pred.get("sql_valid")
        if isinstance(sql_valid, bool):
            successful += int(sql_valid)
            continue

        sql = str(pred.get("sql", "")).strip()
        if not sql:
            continue
        if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
            continue
        if not re.search(r"\bFROM\b", sql, re.IGNORECASE):
            continue

        syntax = validator.validate_syntax(sql)
        completeness = validator.validate_completeness(sql)
        if syntax["valid"] and completeness["complete"]:
            successful += 1

    return successful / len(predictions)


def _ensure_text2sql_prompts(
    predictions: list[dict[str, object]],
    *,
    config: dict,
    model_name: str,
) -> None:
    """Backfill generation prompts so CSV rows match text2sql_details.csv format."""
    for pred in predictions:
        if pred.get("prompt"):
            continue
        question = str(pred.get("question", "")).strip()
        schema = str(pred.get("schema", "")).strip()
        if not question:
            continue
        pred["prompt"] = build_text2sql_prompt(
            question,
            schema,
            config=config,
            model_name=model_name,
        )


def print_metrics(metrics: dict, title: str, prefix: str = "") -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    labels = [
        ("exact_match", "Exact Match Accuracy"),
        ("qwen_correct_rate", "Qwen Correct Rate"),
        ("qwen_overall_correct_rate", "Qwen Overall Correct Rate"),
        ("execution_accuracy", "Execution Accuracy"),
        ("syntax_validity", "Syntax Validity Rate"),
        ("structural_equivalence", "Structural Equivalence"),
        ("translation_success_rate", "Translation Success Rate"),
        ("scored_count", "Scored Sample Count"),
        ("total_count", "Total Sample Count"),
        ("token_f1", "Token F1"),
        ("bleu", "BLEU"),
        ("rouge_l", "ROUGE-L"),
        ("bertscore", "BERTScore"),
        ("codebleu", "CodeBLEU"),
        ("ngram_match", "  CodeBLEU N-gram"),
        ("syntax_match", "  CodeBLEU Syntax"),
        ("semantic_match", "  CodeBLEU Semantic"),
        ("count", "Sample Count"),
        ("qwen_count", "Qwen Sample Count"),
    ]
    for key, label in labels:
        if key in metrics:
            val = metrics[key]
            if val is None:
                continue
            display_label = f"{prefix}{label}" if prefix else label
            if isinstance(val, float):
                print(f"  {display_label:30s}: {val:.4f}")
            else:
                print(f"  {display_label:30s}: {val}")


def run_quick_baseline(max_samples: int, log_mlflow: bool) -> dict:
    """Run baseline on built-in examples + sample DB (fastest start)."""
    from scripts.setup_sample_db import create_sample_db
    from src.text2sql.sql_generator import SQLGenerator

    config = load_config()
    set_seeds(config)
    db_path = create_sample_db(ROOT / "data" / "samples" / "students.db")

    examples = QUICK_REFERENCE[:max_samples]
    generator = SQLGenerator(config=config)
    runner = BenchmarkRunner(
        config=config,
        sql_generator=generator,
        enable_mlflow=log_mlflow,
    )
    runner.max_samples = max_samples

    return runner.run_on_dataset(
        examples,
        dataset_name="quick_reference_baseline",
        db_resolver=lambda _: str(db_path),
    )


def _print_cache_status(dataset: str, config: dict) -> None:
    """Show whether model and dataset will be loaded from local cache."""
    model_dir = get_model_cache_dir(get_model_name(config))
    bert_dir = get_model_cache_dir(get_bertscore_model_name(config))
    data_dir = get_spider_data_dir() if dataset == "spider" else get_bird_data_dir()
    data_cached = is_spider_cached(data_dir) if dataset == "spider" else is_bird_cached(data_dir)

    model_status = "cached" if is_model_cached(model_dir) else "will download"
    bert_status = "cached" if is_model_cached(bert_dir) else "will download"
    data_status = "cached" if data_cached else "will download"
    print(f"Model ({get_model_name(config)}): {model_status} at {model_dir}")
    print(f"BERTScore ({get_bertscore_model_name(config)}): {bert_status} at {bert_dir}")
    print(f"Dataset ({dataset}): {data_status} at {data_dir}")


def run_dataset_baseline(
    dataset: str, split: str, max_samples: int, log_mlflow: bool = False
) -> dict:
    """Run baseline on Spider or BirdBench (downloads data + loads model)."""
    config = load_config()
    config["evaluation"]["max_samples"] = max_samples
    set_seeds(config)
    runner = BenchmarkRunner(config=config, enable_mlflow=log_mlflow)

    if dataset == "spider":
        return runner.run_spider(split)
    if dataset == "bird":
        return runner.run_bird(split)
    raise ValueError(f"Unknown dataset: {dataset}")


def main() -> None:
    import os

    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

    parser = argparse.ArgumentParser(description="Baseline model evaluation")
    parser.add_argument(
        "--dataset",
        choices=["quick", "spider", "bird"],
        default="quick",
        help="quick=builtin examples (fast), spider/bird=full benchmark",
    )
    parser.add_argument("--split", default="validation", help="spider/bird split")
    parser.add_argument("--max-samples", type=int, default=5, help="number of examples")
    parser.add_argument("--mlflow", action="store_true", help="log results to MLflow")
    parser.add_argument(
        "--output",
        default="baseline_eval_results",
        help="run name; creates results/<name>/ with metrics.json and detail CSVs",
    )
    parser.add_argument(
        "--no-qwen",
        action="store_true",
        help="Skip Qwen semantic evaluation for detail CSVs and metrics",
    )
    args = parser.parse_args()

    config = load_config()
    model_name = get_model_name(config)
    qwen_model_name = get_qwen_evaluator_model_name(config)
    print(f"Baseline Evaluation: {model_name}")
    print(f"Qwen Evaluator: {qwen_model_name}")
    print(f"Dataset: {args.dataset} | Max samples: {args.max_samples}")

    if args.dataset == "quick":
        result = run_quick_baseline(args.max_samples, args.mlflow)
    else:
        _print_cache_status(args.dataset, config)
        result = run_dataset_baseline(
            args.dataset, args.split, args.max_samples, log_mlflow=args.mlflow
        )

    print_metrics(
        normalize_task_metrics(result["metrics"], task="text2sql"),
        f"Text-to-SQL ({result['dataset']})",
    )
    if result.get("nosql_metrics"):
        print_metrics(
            normalize_task_metrics(result["nosql_metrics"], task="sql2nosql"),
            f"SQL-to-MongoDB ({result['dataset']})",
        )
    if result.get("doc_metrics"):
        print_metrics(
            normalize_task_metrics(result["doc_metrics"], task="documentation"),
            f"MongoDB Documentation ({result['dataset']})",
        )
    print(f"\n  MLflow run ID: {result.get('mlflow_run_id', 'N/A')}")

    run_dir = resolve_results_run_dir(args.output)
    metrics_path = run_dir / METRICS_JSON
    text2sql_details_path = run_dir / TEXT2SQL_DETAILS_CSV
    sql2nosql_details_path = run_dir / SQL2NOSQL_DETAILS_CSV
    documentation_details_path = run_dir / DOCUMENTATION_DETAILS_CSV

    text2sql_predictions = result.get("predictions", [])
    sql2nosql_predictions = result.get("nosql_predictions", [])
    documentation_predictions = result.get("doc_predictions", [])
    _ensure_text2sql_prompts(
        text2sql_predictions,
        config=config,
        model_name=model_name,
    )
    db_paths = [pred.get("db_path") for pred in text2sql_predictions]

    use_qwen = not args.no_qwen
    qwen_evaluator = None
    if use_qwen:
        qwen_evaluator = QwenEvaluator(model_name=qwen_model_name)

    _, _, qwen_text2sql_metrics = save_text2sql_details_csv(
        text2sql_details_path,
        text2sql_predictions,
        db_paths=db_paths,
        qwen_evaluator=qwen_evaluator,
        use_qwen=use_qwen,
        model_name=model_name,
        config=config,
    )
    _, _, qwen_sql2nosql_metrics = save_sql2nosql_details_csv(
        sql2nosql_details_path,
        sql2nosql_predictions,
        qwen_evaluator=qwen_evaluator,
        use_qwen=use_qwen,
        model_name=model_name,
        config=config,
    )
    _, _, qwen_documentation_metrics = save_documentation_details_csv(
        documentation_details_path,
        documentation_predictions,
        qwen_evaluator=qwen_evaluator,
        use_qwen=use_qwen,
        model_name=model_name,
        config=config,
    )

    text2sql_metrics = merge_qwen_summary_into_metrics(
        result["metrics"],
        qwen_text2sql_metrics if use_qwen else None,
        task="text2sql",
    )
    text2sql_metrics["total_count"] = len(text2sql_predictions)
    text2sql_metrics["scored_count"] = len(text2sql_predictions)
    text2sql_metrics["translation_success_rate"] = (
        _compute_text2sql_translation_success_rate(text2sql_predictions)
    )
    sql2nosql_metrics = merge_qwen_summary_into_metrics(
        result.get("nosql_metrics"),
        qwen_sql2nosql_metrics if use_qwen else None,
        task="sql2nosql",
    )
    documentation_metrics = merge_qwen_summary_into_metrics(
        result.get("doc_metrics"),
        qwen_documentation_metrics if use_qwen else None,
        task="documentation",
    )

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": model_name,
                "evaluator_model": qwen_model_name if use_qwen else None,
                "dataset": result["dataset"],
                "text2sql": text2sql_metrics,
                "sql2nosql": sql2nosql_metrics,
                "documentation": documentation_metrics,
                "mlflow_run_id": result.get("mlflow_run_id"),
            },
            f,
            indent=2,
        )

    if use_qwen:
        qwen_text2sql_only = {
            key: value
            for key, value in text2sql_metrics.items()
            if key.startswith("qwen_")
        }
        qwen_sql2nosql_only = {
            key: value
            for key, value in sql2nosql_metrics.items()
            if key.startswith("qwen_")
        }
        qwen_documentation_only = {
            key: value
            for key, value in documentation_metrics.items()
            if key.startswith("qwen_")
        }
        print_metrics(
            qwen_text2sql_only,
            f"Qwen Text-to-SQL ({result['dataset']})",
        )
        print_metrics(
            qwen_sql2nosql_only,
            f"Qwen SQL-to-MongoDB ({result['dataset']})",
        )
        print_metrics(
            qwen_documentation_only,
            f"Qwen MongoDB Documentation ({result['dataset']})",
        )

    print(f"  Run saved: {run_dir}")
    print(f"    metrics: {metrics_path}")
    print(f"    text2sql details: {text2sql_details_path}")
    print(f"    sql2nosql details: {sql2nosql_details_path}")
    print(f"    documentation details: {documentation_details_path}")
    if args.mlflow:
        print("\nView MLflow UI: mlflow ui --backend-store-uri sqlite:///mlflow.db")


if __name__ == "__main__":
    main()
