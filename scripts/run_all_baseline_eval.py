"""
Run baseline evaluation for all dataset × model combinations.

Models: hardcoded list below (see MODELS).
Datasets: spider, bird.

Output folder name format:
  <dataset>_<model_short_name>_<DDMM>_<HHMM>
  e.g. spider_codegen-350M-multi_1406_1215

Usage:
  python scripts/run_all_baseline_eval.py
  python scripts/run_all_baseline_eval.py --max-samples 10
  python scripts/run_all_baseline_eval.py --dry-run
  python scripts/run_all_baseline_eval.py --list-models
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("bird", "spider")
MODELS = (
    "Salesforce/codegen-350M-multi",
    "bigcode/starcoder2-3b",
    "google-t5/t5-base",
    "google-t5/t5-large",
    "Qwen/Qwen2.5-Coder-0.5B",
)


def short_model_name(model_id: str) -> str:
    """Use the HuggingFace repo tail as the run name segment."""
    return model_id.rsplit("/", 1)[-1]


def build_output_name(dataset: str, model_id: str, when: datetime | None = None) -> str:
    stamp = (when or datetime.now()).strftime("%d%m_%H%M")
    return f"{dataset}_{short_model_name(model_id)}_{stamp}"


def run_eval(
    *,
    dataset: str,
    model_id: str,
    max_samples: int,
    split: str,
    mlflow: bool,
    no_qwen: bool,
    dry_run: bool,
) -> int:
    output = build_output_name(dataset, model_id)
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_baseline_eval.py"),
        "--dataset",
        dataset,
        "--split",
        split,
        "--max-samples",
        str(max_samples),
        "--output",
        output,
    ]
    if mlflow:
        cmd.append("--mlflow")
    if no_qwen:
        cmd.append("--no-qwen")

    env = os.environ.copy()
    env["MODEL_NAME"] = model_id

    print("\n" + "=" * 60)
    print(f"  Dataset: {dataset}")
    print(f"  Model:   {model_id}")
    print(f"  Output:  {output}")
    print("=" * 60)
    print("  Command:", " ".join(cmd))

    if dry_run:
        return 0

    result = subprocess.run(cmd, cwd=ROOT, env=env)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run baseline eval for all dataset × model combinations"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=10,
        help="number of examples per run (default: 10)",
    )
    parser.add_argument("--split", default="validation", help="spider/bird split")
    parser.add_argument("--mlflow", action="store_true", help="log results to MLflow")
    parser.add_argument(
        "--no-qwen",
        action="store_true",
        help="skip Qwen semantic evaluation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print planned runs without executing",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="print hardcoded MODELS list and exit",
    )
    args = parser.parse_args()

    models = list(MODELS)

    if args.list_models:
        print(f"Models ({len(models)}):")
        for model in models:
            print(f"  {model}")
        return 0
    total = len(DATASETS) * len(models)

    print(f"Models ({len(models)}):")
    for model in models:
        print(f"  - {model}")
    print(f"Datasets: {', '.join(DATASETS)}")
    print(f"Total runs: {total}")

    failures: list[str] = []

    for dataset in DATASETS:
        for model_id in models:
            rc = run_eval(
                dataset=dataset,
                model_id=model_id,
                max_samples=args.max_samples,
                split=args.split,
                mlflow=args.mlflow,
                no_qwen=args.no_qwen,
                dry_run=args.dry_run,
            )
            if rc != 0:
                failures.append(f"{dataset} / {model_id} (exit {rc})")

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"  Dry run complete — {total} run(s) planned, none executed.")
    elif failures:
        print(f"  Finished with {len(failures)} failure(s):")
        for item in failures:
            print(f"    - {item}")
    else:
        print(f"  All {total} run(s) completed successfully.")
    print("=" * 60)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
