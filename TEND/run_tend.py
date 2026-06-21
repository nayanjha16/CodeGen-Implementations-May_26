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
from TEND.qwen_doc_generator import QwenDocumentationGenerator
from TEND.qwen_evaluator import QwenTENDEvaluator, get_qwen_evaluator_model_name
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
        "--no-doc",
        action="store_true",
        help="Skip Qwen documentation generation for MongoDB queries.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "HuggingFace model id for evaluation and documentation "
            "(default: QWEN_EVALUATOR_MODEL_NAME)."
        ),
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
    generate_documentation: bool = True,
    model_name: str | None = None,
    output_path: Path | None = None,
    evaluator: QwenTENDEvaluator | None = None,
    doc_generator: QwenDocumentationGenerator | None = None,
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
        generate_documentation=generate_documentation,
        model_name=model_name,
        evaluator=evaluator,
        doc_generator=doc_generator,
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

    model_name = args.model or get_qwen_evaluator_model_name()
    generate_documentation = not args.no_doc
    doc_generator: QwenDocumentationGenerator | None = None
    if generate_documentation:
        print(f"Loading Qwen model for documentation: {model_name}")
        doc_generator = QwenDocumentationGenerator(model_name=model_name)
        doc_generator.load()

    run_tend_split(
        dataset=args.dataset,
        split=split,
        max_samples=args.max_samples,
        evaluate=not args.no_eval,
        generate_documentation=generate_documentation,
        model_name=model_name,
        output_path=args.output,
        doc_generator=doc_generator,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
