#!/usr/bin/env python3
"""Smoke validation for LoRA adapters on the frozen Spider gold validation set."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_ADAPTER_RUN = "v1"
DEFAULT_MAX_SAMPLES = 5


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a small LoRA eval smoke test against spider gold validation.",
    )
    parser.add_argument(
        "--version",
        "--name",
        "--adapter-run",
        dest="adapter_run",
        default=DEFAULT_ADAPTER_RUN,
        help=f"Checkpoint run folder (default: {DEFAULT_ADAPTER_RUN}).",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=DEFAULT_MAX_SAMPLES,
        help=f"Examples to evaluate (default: {DEFAULT_MAX_SAMPLES}).",
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        default=True,
        help="Skip Ollama judge (default for smoke runs).",
    )
    parser.add_argument(
        "--with-judge",
        action="store_true",
        help="Enable Ollama judge (overrides default --no-judge).",
    )
    parser.add_argument("--mlflow", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_baseline_eval.py"),
        "--tend-config",
        "spider",
        "--max-samples",
        str(args.max_samples),
        "--adapter-run",
        args.adapter_run,
    ]
    if args.mlflow:
        cmd.append("--mlflow")
    if not args.with_judge:
        cmd.append("--no-judge")

    print("LoRA validation smoke test")
    print(f"  adapter_run: {args.adapter_run}")
    print(f"  max_samples: {args.max_samples}")
    print(f"  command: {' '.join(cmd)}")

    if args.dry_run:
        return 0

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
