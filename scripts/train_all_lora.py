#!/usr/bin/env python3
"""Train LoRA adapters for all tasks (text2sql, sql2nosql, nosql2doc)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if not hasattr(sys.stdout, "isatty"):
    sys.stdout.isatty = lambda: False

from src.datasets.tend_loader import GOLD_VALIDATION_DATASET_NAME, load_gold_validation
from src.training.adapter_verify import verify_all_adapters
from src.training.lora_trainer import train_lora
from src.training.tasks import TRAINING_TASKS
from src.utils.config import get_model_name, load_config
from src.utils.device import resolve_device
from src.utils.logging import setup_logging
from src.utils.paths import build_results_run_name, get_models_checkpoints_dir, resolve_adapter_run_name

DEFAULT_TASK_ORDER = ("text2sql", "sql2nosql", "nosql2doc")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train LoRA adapters for one or more tasks sequentially.",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=sorted(TRAINING_TASKS),
        default=list(DEFAULT_TASK_ORDER),
        help="Tasks to train (default: all three).",
    )
    parser.add_argument("--train-csv", default=None, help="Optional training CSV/JSONL.")
    parser.add_argument("--eval-csv", default=None, help="Optional eval CSV/JSONL.")
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--no-mlflow", action="store_true")
    parser.add_argument(
        "--checkpoint-suite",
        default=None,
        help="Optional subdirectory under models/checkpoints/ for all task outputs.",
    )
    parser.add_argument(
        "--run-baseline",
        action="store_true",
        help="Run baseline eval (codegen-350M, no adapter) before training.",
    )
    parser.add_argument(
        "--baseline-max-samples",
        type=int,
        default=None,
        help=(
            "Limit samples for baseline eval when --run-baseline is set "
            f"(default: full {GOLD_VALIDATION_DATASET_NAME} set)."
        ),
    )
    parser.add_argument(
        "--baseline-no-judge",
        action="store_true",
        help="Skip Ollama judge during baseline eval (--run-baseline).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned runs without training.",
    )
    parser.add_argument(
        "--version",
        "--name",
        dest="run",
        default=None,
        help="Checkpoint run folder under models/checkpoints/ (default: DDMM, e.g. 2506).",
    )
    return parser


def _default_baseline_max_samples() -> int:
    return len(load_gold_validation())


def _run_baseline(
    config_path: Path | None,
    max_samples: int,
    *,
    model_name: str,
    no_judge: bool = False,
) -> tuple[int, str]:
    output_name = build_results_run_name(
        dataset=GOLD_VALIDATION_DATASET_NAME,
        model_name=model_name,
    )
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_baseline_eval.py"),
        "--tend-config",
        "spider",
        "--max-samples",
        str(max_samples),
        "--output",
        output_name,
        "--mlflow",
    ]
    if config_path is not None:
        cmd.extend(["--config", str(config_path)])
    if no_judge:
        cmd.append("--no-judge")
    print("Running baseline eval:", " ".join(cmd))
    rc = subprocess.call(cmd)
    return rc, output_name


def main() -> int:
    setup_logging()
    args = build_parser().parse_args()
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)
    model_name = get_model_name(config)
    run_name = resolve_adapter_run_name(args.run)
    run_dir = get_models_checkpoints_dir() / run_name
    started_at = datetime.now(timezone.utc).isoformat()
    device_request = args.device or config.get("model", {}).get("device", "auto")
    resolved_device = resolve_device(device_request)

    if args.dry_run:
        print(f"Model: {model_name}")
        print(f"Device: {resolved_device} (requested: {device_request})")
        print(f"Checkpoint run: {run_name}")
        for task in args.tasks:
            print(f"  would train: {task} -> models/checkpoints/{run_name}/{task}/")
        if args.run_baseline:
            baseline_samples = args.baseline_max_samples or _default_baseline_max_samples()
            print(
                f"  would baseline: {GOLD_VALIDATION_DATASET_NAME} "
                f"({baseline_samples} samples, no adapter)"
            )
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "train_all_lora.log"
    log_handle = log_path.open("a", encoding="utf-8")
    print(f"Logging to {log_path}")

    class _Tee:
        def __init__(self, *streams):
            self._streams = streams

        def write(self, data: str) -> None:
            for stream in self._streams:
                stream.write(data)
                stream.flush()

        def flush(self) -> None:
            for stream in self._streams:
                stream.flush()

    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = _Tee(stdout, log_handle)
    sys.stderr = _Tee(stderr, log_handle)

    baseline_output: str | None = None
    try:
        print(f"\n=== LoRA training batch ===")
        print(f"Model: {model_name}")
        print(f"Device: {resolved_device} (requested: {device_request})")
        print(f"Checkpoint run: {run_name}")
        print(f"Started: {started_at}")

        if args.run_baseline:
            baseline_samples = args.baseline_max_samples or _default_baseline_max_samples()
            baseline_rc, baseline_output = _run_baseline(
                config_path,
                baseline_samples,
                model_name=model_name,
                no_judge=args.baseline_no_judge,
            )
            if baseline_rc != 0:
                print(f"Baseline eval failed with exit code {baseline_rc}")
                return baseline_rc

        summary_tasks: list[dict] = []
        for task in args.tasks:
            print(f"\n=== Training {task} ===")
            if args.checkpoint_suite:
                out_dir = str(
                    get_models_checkpoints_dir() / args.checkpoint_suite.strip("/") / task
                )
            else:
                out_dir = None
            result = train_lora(
                task,
                config=config,
                train_csv=args.train_csv,
                eval_csv=args.eval_csv,
                output_dir=out_dir,
                max_samples=args.max_samples,
                device=args.device,
                epochs=args.epochs,
                run=args.run,
                enable_mlflow=not args.no_mlflow,
            )
            summary_tasks.append(
                {
                    "task": result.task,
                    "checkpoint_run": result.checkpoint_run,
                    "train_rows": result.train_rows,
                    "eval_rows": result.eval_rows,
                    "train_loss": result.train_loss,
                    "eval_loss": result.eval_loss,
                    "best_eval_loss": result.best_eval_loss,
                    "train_runtime_seconds": result.train_runtime,
                    "adapter_path": str(result.output_dir),
                    "mlflow_run_id": result.mlflow_run_id,
                    "metadata_path": str(result.metadata_path),
                }
            )
            print(f"Done {task}: adapter={result.output_dir}")

        verify = verify_all_adapters(config=config, run=args.run or args.checkpoint_suite)
        failed = [task for task, res in verify.items() if not res.ok]
        if failed:
            print("Adapter verification failed for:", ", ".join(failed))
            for task in failed:
                res = verify[task]
                print(f"  {task}: missing={res.missing_files} errors={res.errors}")
            return 1

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = run_dir / f"training_summary_{stamp}.json"
        summary_payload = {
            "checkpoint_run": run_name,
            "model_name": model_name,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "max_samples": args.max_samples,
            "epochs": args.epochs,
            "baseline_results_run": baseline_output,
            "tasks": summary_tasks,
        }
        summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
        print(f"\nAll adapters verified. Summary: {summary_path}")
        return 0
    finally:
        sys.stdout = stdout
        sys.stderr = stderr
        log_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
