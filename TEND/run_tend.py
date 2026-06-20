#!/usr/bin/env python3
"""CLI entry point for TEND dataset generation and Qwen evaluation."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from TEND.build_tend_dataset import TENDDatasetBuilder
from TEND.paths import ensure_project_on_path, get_tend_output_dir
from TEND.qwen_evaluator import DEFAULT_MODEL, QwenTENDEvaluator
from TEND.spider_source import SpiderSource
from src.sql2nosql.translator import SQLToNoSQLTranslator


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate TEND-style SQL/NoSQL datasets and evaluate with Qwen."
    )
    parser.add_argument(
        "--dataset",
        default="spider",
        choices=["spider"],
        help="Source dataset (spider first; bird later).",
    )
    parser.add_argument(
        "--split",
        default="train",
        choices=["train", "validation", "dev", "test"],
        help="Dataset split to process.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of samples; default processes all available rows.",
    )
    parser.add_argument(
        "--no-eval",
        action="store_true",
        help="Skip Qwen evaluation and only generate converted dataset rows.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="HuggingFace model id for evaluation.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output CSV path (default: data/TEND/<auto-name>.csv).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def run_tend_split(
    *,
    dataset: str,
    split: str,
    max_samples: int | None = None,
    evaluate: bool = True,
    model_name: str = DEFAULT_MODEL,
    output_path: Path | None = None,
    evaluator: QwenTENDEvaluator | None = None,
    spider_source: SpiderSource | None = None,
    tables_by_db: dict[str, dict[str, Any]] | None = None,
    translator: SQLToNoSQLTranslator | None = None,
) -> Path:
    """Generate one TEND split CSV, reusing optional shared resources."""
    builder = TENDDatasetBuilder(
        dataset=dataset,
        split=split,
        max_samples=max_samples,
        evaluate=evaluate,
        model_name=model_name,
        evaluator=evaluator,
        spider_source=spider_source,
        tables_by_db=tables_by_db,
        translator=translator,
    )
    csv_path = builder.build(output_path=output_path)

    summary = TENDDatasetBuilder.summarize_csv(csv_path)
    summary_path = csv_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Summary saved: {summary_path}")
    return csv_path


def main(argv: list[str] | None = None) -> int:
    ensure_project_on_path()
    args = parse_args(argv)
    _configure_logging(args.verbose)

    split = "validation" if args.split == "dev" else args.split
    output_dir = get_tend_output_dir()
    print(f"TEND output directory: {output_dir}")

    run_tend_split(
        dataset=args.dataset,
        split=split,
        max_samples=args.max_samples,
        evaluate=not args.no_eval,
        model_name=args.model,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
