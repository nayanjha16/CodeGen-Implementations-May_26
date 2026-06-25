#!/usr/bin/env python3
"""Train a LoRA adapter for text2sql, sql2nosql, or nosql2doc."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.lora_trainer import train_lora
from src.training.tasks import TRAINING_TASKS
from src.utils.config import get_adapter_path, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a LoRA adapter for one task.")
    parser.add_argument(
        "--task",
        required=True,
        choices=sorted(TRAINING_TASKS),
        help="Fine-tuning task (text2sql, sql2nosql, nosql2doc).",
    )
    parser.add_argument(
        "--train-csv",
        default=None,
        help="Optional CSV/JSONL path for training rows (default: HF spider+bird train).",
    )
    parser.add_argument(
        "--eval-csv",
        default=None,
        help="Optional CSV/JSONL path for eval rows (default: HF spider+bird test).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Adapter output directory (default: models/checkpoints/<run>/<task>/).",
    )
    parser.add_argument(
        "--version",
        "--name",
        dest="run",
        default=None,
        help="Checkpoint run folder under models/checkpoints/ (default: DDMM, e.g. 2506).",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit rows for smoke/debug runs.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override training.epochs from config.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Device override: auto, cuda, mps, or cpu.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/default.yaml).",
    )
    parser.add_argument(
        "--no-mlflow",
        action="store_true",
        help="Disable MLflow logging.",
    )


def main() -> int:
    args = build_parser().parse_args()
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)

    output_dir = args.output_dir or str(get_adapter_path(args.task, config, run=args.run))

    result = train_lora(
        args.task,
        config=config,
        train_csv=args.train_csv,
        eval_csv=args.eval_csv,
        output_dir=output_dir,
        run=args.run,
        max_samples=args.max_samples,
        device=args.device,
        epochs=args.epochs,
        enable_mlflow=not args.no_mlflow,
    )

    print(f"Task: {result.task}")
    print(f"Train rows: {result.train_rows}")
    print(f"Eval rows: {result.eval_rows}")
    print(f"Train loss: {result.train_loss}")
    print(f"Eval loss: {result.eval_loss}")
    print(f"Best eval loss: {result.best_eval_loss}")
    print(f"Adapter: {result.output_dir}")
    print(f"Metadata: {result.metadata_path}")
    if result.mlflow_run_id:
        print(f"MLflow run: {result.mlflow_run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
