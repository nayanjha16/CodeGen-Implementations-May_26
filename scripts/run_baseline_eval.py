"""
Baseline model evaluation for Salesforce/codegen-350M-multi.

Computes: Exact Match, Execution Accuracy, Syntax Validity,
          BLEU, ROUGE-L, BERTScore, CodeBLEU

Usage:
  python scripts/run_baseline_eval.py                    # 5 samples, built-in reference data (fast)
  python scripts/run_baseline_eval.py --dataset spider   # Spider validation split
  python scripts/run_baseline_eval.py --dataset bird     # BirdBench validation split
  python scripts/run_baseline_eval.py --max-samples 20   # limit samples
  python scripts/run_baseline_eval.py --mlflow           # log to MLflow
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.benchmark import BenchmarkRunner
from evaluation.metrics import EvaluationMetrics
from evaluation.mlflow_tracker import MLflowTracker
from src.utils.config import load_config
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


def print_metrics(metrics: dict, title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    labels = [
        ("exact_match", "Exact Match Accuracy"),
        ("execution_accuracy", "Execution Accuracy"),
        ("syntax_validity", "Syntax Validity Rate"),
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
            if isinstance(val, float):
                print(f"  {label:30s}: {val:.4f}")
            else:
                print(f"  {label:30s}: {val}")


def run_quick_baseline(max_samples: int, log_mlflow: bool) -> dict:
    """Run baseline on built-in examples + sample DB (fastest start)."""
    from scripts.setup_sample_db import create_sample_db
    from src.text2sql.sql_generator import SQLGenerator

    config = load_config()
    set_seeds(config)
    db_path = create_sample_db(ROOT / "data" / "sample" / "students.db")

    examples = QUICK_REFERENCE[:max_samples]
    generator = SQLGenerator(config=config)
    runner = BenchmarkRunner(config=config, sql_generator=generator)
    runner.max_samples = max_samples

    return runner.run_on_dataset(
        examples,
        dataset_name="quick_reference_baseline",
        db_resolver=lambda _: str(db_path),
    )


def run_dataset_baseline(dataset: str, split: str, max_samples: int) -> dict:
    """Run baseline on Spider or BirdBench (downloads data + loads model)."""
    config = load_config()
    config["evaluation"]["max_samples"] = max_samples
    set_seeds(config)
    runner = BenchmarkRunner(config=config)

    if dataset == "spider":
        return runner.run_spider(split)
    if dataset == "bird":
        return runner.run_bird(split)
    raise ValueError(f"Unknown dataset: {dataset}")


def main() -> None:
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
        default=str(ROOT / "data" / "baseline_eval_results.json"),
        help="save metrics JSON here",
    )
    args = parser.parse_args()

    print("Baseline Evaluation: Salesforce/codegen-350M-multi")
    print(f"Dataset: {args.dataset} | Max samples: {args.max_samples}")

    if args.dataset == "quick":
        result = run_quick_baseline(args.max_samples, args.mlflow)
    else:
        print("Note: First run downloads model (~700MB) and dataset.")
        result = run_dataset_baseline(args.dataset, args.split, args.max_samples)

    print_metrics(result["metrics"], f"Baseline Results ({result['dataset']})")
    print(f"\n  MLflow run ID: {result.get('mlflow_run_id', 'N/A')}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": "Salesforce/codegen-350M-multi",
                "dataset": result["dataset"],
                "metrics": result["metrics"],
                "mlflow_run_id": result.get("mlflow_run_id"),
            },
            f,
            indent=2,
        )
    print(f"  Results saved: {output_path}")
    print("\nView MLflow UI: mlflow ui --backend-store-uri mlruns")


if __name__ == "__main__":
    main()
