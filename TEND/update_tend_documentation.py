#!/usr/bin/env python3
"""
Backfill MongoDB query documentation in existing TEND CSV files under data/TEND.

Uses the Qwen evaluator model (``QWEN_EVALUATOR_MODEL_NAME``) to generate a
plain-English ``documentation`` column from each row's ``nosql_query`` and
``nosql_schema``.

Usage:
  python -m TEND.update_tend_documentation
  python -m TEND.update_tend_documentation --input data/TEND/spider_validation_0614_1815.csv
  python -m TEND.update_tend_documentation --all --max-samples 10
  python -m TEND.update_tend_documentation --all --force
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

from TEND.build_tend_dataset import TENDDatasetBuilder
from TEND.paths import ensure_project_on_path, get_tend_output_dir
from TEND.qwen_doc_generator import QwenDocumentationGenerator
from TEND.qwen_evaluator import get_qwen_evaluator_model_name


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def _discover_csv_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.csv") if path.is_file())


def _resolve_inputs(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return _discover_csv_files(get_tend_output_dir())
    if args.input:
        paths = [Path(path) for path in args.input]
        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"TEND CSV not found: {path}")
        return paths
    default_dir = get_tend_output_dir()
    discovered = _discover_csv_files(default_dir)
    if not discovered:
        raise FileNotFoundError(
            f"No CSV files found under {default_dir}. Pass --input or --all."
        )
    return discovered


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add or refresh MongoDB query documentation in TEND CSV files."
    )
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        help="One or more TEND CSV paths to update.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update every CSV file under data/TEND.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path when updating a single input CSV.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Write a .bak copy before overwriting an input CSV in place.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate documentation even when the column is already filled.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit rows processed per CSV.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override HuggingFace model id (default: QWEN_EVALUATOR_MODEL_NAME).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ensure_project_on_path()
    args = parse_args(argv)
    _configure_logging(args.verbose)

    if args.output and (args.all or (args.input and len(args.input) > 1)):
        raise SystemExit("--output can only be used with a single --input CSV.")

    try:
        csv_paths = _resolve_inputs(args)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    model_name = args.model or get_qwen_evaluator_model_name()
    print(f"TEND output directory: {get_tend_output_dir()}")
    print(f"Files to update: {len(csv_paths)}")
    print(f"Model: {model_name} (QWEN_EVALUATOR_MODEL_NAME)")

    doc_generator = QwenDocumentationGenerator(model_name=model_name)
    print("\nLoading Qwen model ...")
    doc_generator.load()
    print("Model loaded and ready.\n")

    failures: list[str] = []
    for csv_path in csv_paths:
        print("=" * 60)
        print(f"Updating: {csv_path}")
        print("=" * 60)
        try:
            output_path = args.output if len(csv_paths) == 1 else None
            if output_path is None and args.backup and csv_path.exists():
                backup_path = csv_path.with_suffix(csv_path.suffix + ".bak")
                shutil.copy2(csv_path, backup_path)
                print(f"Backup written: {backup_path}")

            TENDDatasetBuilder.update_csv_documentation(
                csv_path,
                doc_generator,
                output_path=output_path,
                force=args.force,
                max_samples=args.max_samples,
            )
        except Exception as exc:
            failures.append(f"{csv_path} ({exc})")
            print(f"ERROR: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print(f"Finished with {len(failures)} failure(s):")
        for item in failures:
            print(f"  - {item}")
    else:
        print(f"Updated {len(csv_paths)} file(s) successfully.")
    print("=" * 60)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
