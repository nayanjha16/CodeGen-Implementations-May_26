"""
Run baseline evaluation for all model combinations on the Spider gold validation set.

Models: hardcoded list below (see MODELS).
Dataset: data/spider_gold_validation.jsonl (50 frozen examples).

Output folder name format:
  spider_gold_validation_<model_short_name>_<DDMM>_<HHMM>
  e.g. spider_gold_validation_codegen-350M-multi_2506_2024

Usage:
  python scripts/run_all_baseline_eval.py
  python scripts/run_all_baseline_eval.py --max-samples 50
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
sys.path.insert(0, str(ROOT))

from src.datasets.tend_loader import GOLD_VALIDATION_DATASET_NAME
from src.utils.paths import build_results_run_name

MODELS = (
    "Salesforce/codegen-350M-multi",
    # "bigcode/starcoder2-3b",
    # "google-t5/t5-base",
    # "google-t5/t5-large",
    "Qwen/Qwen2.5-Coder-0.5B",
)


def build_output_name(
    model_id: str,
    when: datetime | None = None,
) -> str:
    return build_results_run_name(
        dataset=GOLD_VALIDATION_DATASET_NAME,
        model_name=model_id,
        when=when,
    )


def run_eval(
    *,
    model_id: str,
    max_samples: int,
    mlflow: bool,
    no_judge: bool,
    dry_run: bool,
    when: datetime | None = None,
) -> int:
    output = build_output_name(model_id, when=when)
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_baseline_eval.py"),
        "--tend-config",
        "spider",
        "--max-samples",
        str(max_samples),
        "--output",
        output,
    ]
    if mlflow:
        cmd.append("--mlflow")
    if no_judge:
        cmd.append("--no-judge")

    env = os.environ.copy()
    env["MODEL_NAME"] = model_id

    print("\n" + "=" * 60)
    print(f"  Dataset:     {GOLD_VALIDATION_DATASET_NAME}")
    print(f"  Model:       {model_id}")
    print(f"  Max samples: {max_samples}")
    print(f"  Output:      {output}")
    print("=" * 60)
    print("  Command:", " ".join(cmd))

    if dry_run:
        return 0

    result = subprocess.run(cmd, cwd=ROOT, env=env)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run baseline eval for all models on Spider gold validation"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=50,
        help="number of examples per run (default: 50, full gold set)",
    )
    parser.add_argument("--mlflow", action="store_true", help="log results to MLflow")
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="skip Ollama semantic judge",
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
    total = len(models)
    batch_time = datetime.now()

    print(f"Dataset: {GOLD_VALIDATION_DATASET_NAME}")
    print(f"Models ({len(models)}):")
    for model in models:
        print(f"  - {model}")
    print(f"Total runs: {total}")

    failures: list[str] = []

    for model_id in models:
        rc = run_eval(
            model_id=model_id,
            max_samples=args.max_samples,
            mlflow=args.mlflow,
            no_judge=args.no_judge,
            dry_run=args.dry_run,
            when=batch_time,
        )
        if rc != 0:
            failures.append(f"{model_id} (exit {rc})")

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
