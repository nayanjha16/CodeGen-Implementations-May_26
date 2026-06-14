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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation.benchmark import BenchmarkRunner
from src.evaluation.export import (
    METRICS_JSON,
    SQL2NOSQL_DETAILS_CSV,
    TEXT2SQL_DETAILS_CSV,
    save_sql2nosql_details_csv,
    save_text2sql_details_csv,
)
from src.models.model_loader import is_model_cached
from src.utils.config import get_bertscore_model_name, get_model_name, load_config
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


def print_metrics(metrics: dict, title: str, prefix: str = "") -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    labels = [
        ("exact_match", "Exact Match Accuracy"),
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
    ]
    for key, label in labels:
        if key in metrics:
            val = metrics[key]
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
    args = parser.parse_args()

    config = load_config()
    model_name = get_model_name(config)
    print(f"Baseline Evaluation: {model_name}")
    print(f"Dataset: {args.dataset} | Max samples: {args.max_samples}")

    if args.dataset == "quick":
        result = run_quick_baseline(args.max_samples, args.mlflow)
    else:
        _print_cache_status(args.dataset, config)
        result = run_dataset_baseline(
            args.dataset, args.split, args.max_samples, log_mlflow=args.mlflow
        )

    print_metrics(result["metrics"], f"Text-to-SQL Results ({result['dataset']})")
    if result.get("nosql_metrics"):
        print_metrics(
            result["nosql_metrics"],
            f"SQL-to-MongoDB Results ({result['dataset']})",
        )
    print(f"\n  MLflow run ID: {result.get('mlflow_run_id', 'N/A')}")

    run_dir = resolve_results_run_dir(args.output)
    metrics_path = run_dir / METRICS_JSON
    text2sql_details_path = run_dir / TEXT2SQL_DETAILS_CSV
    sql2nosql_details_path = run_dir / SQL2NOSQL_DETAILS_CSV

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": model_name,
                "dataset": result["dataset"],
                "text2sql": result["metrics"],
                "sql2nosql": result.get("nosql_metrics"),
                "mlflow_run_id": result.get("mlflow_run_id"),
            },
            f,
            indent=2,
        )

    text2sql_predictions = result.get("predictions", [])
    sql2nosql_predictions = result.get("nosql_predictions", [])
    db_paths = [pred.get("db_path") for pred in text2sql_predictions]
    save_text2sql_details_csv(
        text2sql_details_path,
        text2sql_predictions,
        db_paths=db_paths,
    )
    save_sql2nosql_details_csv(sql2nosql_details_path, sql2nosql_predictions)

    print(f"  Run saved: {run_dir}")
    print(f"    metrics: {metrics_path}")
    print(f"    text2sql details: {text2sql_details_path}")
    print(f"    sql2nosql details: {sql2nosql_details_path}")
    if args.mlflow:
        print("\nView MLflow UI: mlflow ui --backend-store-uri sqlite:///mlflow.db")


if __name__ == "__main__":
    main()
