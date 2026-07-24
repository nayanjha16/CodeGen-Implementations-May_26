#!/usr/bin/env python3
"""Verify LoRA adapter artifacts for trained tasks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.adapter_verify import verify_all_adapters, verify_adapter_dir
from src.training.tasks import TRAINING_TASKS
from src.utils.config import get_adapter_path, load_config
from src.utils.logging import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify LoRA adapter directories.")
    parser.add_argument(
        "--task",
        choices=sorted(TRAINING_TASKS),
        default=None,
        help="Verify a single task (default: all tasks).",
    )
    parser.add_argument(
        "--no-require-metadata",
        action="store_true",
        help="Do not require run_metadata.json.",
    )
    parser.add_argument("--config", default=None)
    parser.add_argument(
        "--version",
        "--name",
        dest="run",
        default=None,
        help="Checkpoint run under models/checkpoints/<model>/ (default: DDMM or MODEL_ADAPTER_RUN).",
    )
    return parser


def main() -> int:
    setup_logging()
    args = build_parser().parse_args()
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)
    require_metadata = not args.no_require_metadata

    if args.task:
        result = verify_adapter_dir(
            args.task,
            adapter_path=get_adapter_path(args.task, config, run=args.run),
            config=config,
            require_metadata=require_metadata,
        )
        results = {args.task: result}
    else:
        results = verify_all_adapters(
            config=config,
            run=args.run,
            require_metadata=require_metadata,
        )

    exit_code = 0
    for task, result in results.items():
        status = "OK" if result.ok else "FAIL"
        print(f"{status} {task}: {result.adapter_path}")
        if result.missing_files:
            print(f"  missing: {', '.join(result.missing_files)}")
        for error in result.errors:
            print(f"  error: {error}")
        if result.metadata:
            print(
                f"  train_loss={result.metadata.get('train_loss')} "
                f"eval_loss={result.metadata.get('eval_loss')} "
                f"best_eval={result.metadata.get('best_eval_loss')}"
            )
        if not result.ok:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
