"""
Baseline model evaluation.

Uses the frozen Spider gold validation set (data/spider_gold_validation.jsonl)
for all baseline runs.

Evaluates three independent tasks on gold dataset rows:
  text2sql (question + schema), sql2nosql (gold sql), nosql2doc (gold nosql_query).

Metrics:
  text2sql / sql2nosql: execution_accuracy, exact_match, structural_similarity
  documentation: exact_match, embedding_similarity, judge_score

Usage:
  python scripts/run_baseline_eval.py
  python scripts/run_baseline_eval.py --max-samples 20
  python scripts/run_baseline_eval.py --mlflow
  python scripts/run_baseline_eval.py --output spider_gold_baseline
  python scripts/run_baseline_eval.py --full-split --split test
  python scripts/run_baseline_eval.py --no-judge
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets.tend_loader import GOLD_VALIDATION_DATASET_NAME, load_gold_validation
from src.evaluation.database_execution import is_database_available
from src.evaluation.benchmark import BenchmarkRunner
from src.evaluation.export import (
    DOCUMENTATION_DETAILS_CSV,
    METRICS_JSON,
    SQL2NOSQL_DETAILS_CSV,
    TEXT2SQL_DETAILS_CSV,
    merge_judge_summary_into_metrics,
    normalize_task_metrics,
    run_documentation_judge,
    save_documentation_details_csv,
    save_sql2nosql_details_csv,
    save_text2sql_details_csv,
)
from src.llm.factory import create_judge
from src.models.model_loader import is_model_cached
from src.text2sql.sql_executor import build_text2sql_prompt
from src.utils.config import (
    get_adapter_path,
    get_judge_model,
    get_llm_provider,
    get_model_name,
    load_config,
)
from src.utils.paths import (
    build_results_run_name,
    get_model_cache_dir,
    resolve_results_run_dir,
)
from src.utils.logging import setup_logging
from src.utils.seeds import set_seeds


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


def print_metrics(metrics: dict, title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key:30s}: {value:.4f}")
        else:
            print(f"  {key:30s}: {value}")


def run_tend_baseline(
    tend_config: str,
    split: str,
    max_samples: int,
    log_mlflow: bool = False,
    *,
    use_gold_validation: bool = True,
    adapter_run: str | None = None,
    device: str | None = None,
) -> dict:
    """Run baseline on TEND data (Spider gold validation by default)."""
    config = load_config()
    config["evaluation"]["max_samples"] = max_samples
    if device is not None:
        config.setdefault("model", {})["device"] = device
    set_seeds(config)
    runner = BenchmarkRunner(
        config=config,
        enable_mlflow=log_mlflow,
        adapter_run=adapter_run,
    )
    return runner.run_tend(
        config=tend_config,
        split=split,
        use_gold_validation=use_gold_validation,
    )


def main() -> None:
    import os

    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    setup_logging()

    parser = argparse.ArgumentParser(description="Baseline model evaluation")
    parser.add_argument(
        "--tend-config",
        choices=["spider", "bird"],
        default="spider",
        help="TEND subset (default: spider; uses gold validation for spider)",
    )
    parser.add_argument(
        "--split",
        default="test",
        help="TEND split when --full-split is set (test = source validation/dev)",
    )
    parser.add_argument(
        "--full-split",
        action="store_true",
        help="Evaluate the full Hugging Face split instead of gold validation",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=50,
        help="number of examples (default: 50, full gold validation set)",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Device override: auto, cuda, mps, dml, or cpu.",
    )
    parser.add_argument("--mlflow", action="store_true", help="log results to MLflow")
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Run folder name under results/; default auto-generates "
            "tend_<config>_<split>_<model>_<DDMM>_<HHMM>"
        ),
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip LLM judge for documentation metrics",
    )
    parser.add_argument(
        "--version",
        "--name",
        "--adapter-run",
        dest="adapter_run",
        default=None,
        help="LoRA checkpoint run under models/checkpoints/<run>/ (e.g. v1).",
    )
    args = parser.parse_args()

    config = load_config()
    model_name = get_model_name(config)
    judge_model_name = get_judge_model(config)
    llm_provider = get_llm_provider(config)
    use_gold_validation = args.tend_config == "spider" and not args.full_split
    if use_gold_validation:
        gold_count = len(load_gold_validation())
        dataset_label = GOLD_VALIDATION_DATASET_NAME
    else:
        gold_count = None
        dataset_label = f"tend_{args.tend_config}_{args.split}"
    output_name = args.output or build_results_run_name(
        dataset=dataset_label,
        model_name=(
            f"{model_name.split('/')[-1]}_lora-{args.adapter_run}"
            if args.adapter_run
            else model_name
        ),
    )
    eval_label = "LoRA Evaluation" if args.adapter_run else "Baseline Evaluation"
    print(f"{eval_label}: {model_name}")
    if args.adapter_run:
        print(f"Adapter run: {args.adapter_run}")
        for task in ("text2sql", "sql2nosql", "nosql2doc"):
            print(f"  {task}: {get_adapter_path(task, config, run=args.adapter_run)}")
    print(f"Documentation judge ({llm_provider}): {judge_model_name}")
    print(f"Database execution available: {is_database_available()}")
    if use_gold_validation:
        print(
            f"Dataset: {GOLD_VALIDATION_DATASET_NAME} "
            f"({gold_count} examples) | Max samples: {args.max_samples}"
        )
    else:
        print(
            f"TEND config: {args.tend_config} | Split: {args.split} | "
            f"Max samples: {args.max_samples}"
        )
    print(f"Results folder: {output_name}")

    model_dir = get_model_cache_dir(get_model_name(config))
    model_status = "cached" if is_model_cached(model_dir) else "will download"
    print(f"Model ({get_model_name(config)}): {model_status} at {model_dir}")
    if use_gold_validation:
        print("Evaluation set: data/spider_gold_validation.jsonl")
    else:
        print(
            f"TEND dataset: care2achieve/tend config={args.tend_config} "
            f"split={args.split}"
        )
    result = run_tend_baseline(
        args.tend_config,
        args.split,
        args.max_samples,
        log_mlflow=args.mlflow,
        use_gold_validation=use_gold_validation,
        adapter_run=args.adapter_run,
        device=args.device,
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

    run_dir = resolve_results_run_dir(output_name)
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

    use_judge = not args.no_judge
    judge = create_judge(config) if use_judge else None

    judge_results: list[dict[str, object]] = []
    judge_documentation_metrics: dict[str, object] = {}
    if use_judge:
        judge_results, judge_documentation_metrics = run_documentation_judge(
            documentation_predictions,
            judge=judge,
            use_judge=True,
            config=config,
        )

    text2sql_metrics = normalize_task_metrics(result["metrics"], task="text2sql")
    sql2nosql_metrics = normalize_task_metrics(result.get("nosql_metrics"), task="sql2nosql")
    documentation_metrics = merge_judge_summary_into_metrics(
        result.get("doc_metrics"),
        judge_documentation_metrics if use_judge else None,
        task="documentation",
    )

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": model_name,
                "adapter_run": args.adapter_run,
                "run_type": "lora" if args.adapter_run else "baseline",
                "judge_model": judge_model_name if use_judge else None,
                "database_execution": is_database_available(),
                "dataset": result["dataset"],
                "text2sql": text2sql_metrics,
                "sql2nosql": sql2nosql_metrics,
                "documentation": documentation_metrics,
                "mlflow_run_id": result.get("mlflow_run_id"),
            },
            f,
            indent=2,
        )

    save_text2sql_details_csv(
        text2sql_details_path,
        text2sql_predictions,
        model_name=model_name,
        config=config,
    )
    save_sql2nosql_details_csv(
        sql2nosql_details_path,
        sql2nosql_predictions,
        model_name=model_name,
        config=config,
    )
    save_documentation_details_csv(
        documentation_details_path,
        documentation_predictions,
        judge=judge,
        use_judge=use_judge,
        model_name=model_name,
        config=config,
        judge_results=judge_results if use_judge else None,
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
