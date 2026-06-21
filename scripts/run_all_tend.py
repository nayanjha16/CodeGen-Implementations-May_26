"""
Run TEND dataset generation for train and validation splits.

Loads Qwen, Spider tables, and the SQL translator once and reuses them
across all splits in a single process.

Usage:
  python scripts/run_all_tend.py
  python scripts/run_all_tend.py --max-samples 10
  python scripts/run_all_tend.py --no-eval
  python scripts/run_all_tend.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sql2nosql.translator import SQLToNoSQLTranslator

from TEND.paths import get_tend_output_dir
from TEND.qwen_doc_generator import QwenDocumentationGenerator
from TEND.qwen_evaluator import QwenTENDEvaluator, get_qwen_evaluator_model_name
from TEND.run_tend import run_tend_split
from TEND.spider_source import SpiderSource

DEFAULT_SPLITS = ("train", "validation")


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run TEND dataset generation for train and validation splits."
    )
    parser.add_argument(
        "--dataset",
        default="spider",
        choices=["spider"],
        help="Source dataset (default: spider).",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=list(DEFAULT_SPLITS),
        choices=["train", "validation", "dev", "test"],
        help="Splits to process (default: train validation).",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit rows per split; default processes all available rows.",
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
        help="HuggingFace model id (default: QWEN_EVALUATOR_MODEL_NAME).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging for each run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned runs without executing.",
    )
    args = parser.parse_args()

    _configure_logging(args.verbose)

    splits = ["validation" if split == "dev" else split for split in args.splits]
    model_name = args.model or get_qwen_evaluator_model_name()
    evaluate = not args.no_eval
    generate_documentation = not args.no_doc
    total = len(splits)

    print(f"TEND output directory: {get_tend_output_dir()}")
    print(f"Dataset: {args.dataset}")
    print(f"Splits:  {', '.join(splits)}")
    print(f"Total runs: {total}")
    if evaluate:
        print(f"Model:   {model_name} (loaded once, shared across splits)")
    else:
        print("Evaluation: disabled (--no-eval)")
    if generate_documentation:
        print(f"Documentation: enabled with {model_name}")
    else:
        print("Documentation: disabled (--no-doc)")

    if args.dry_run:
        for split in splits:
            print("\n" + "=" * 60)
            print(f"  Dataset: {args.dataset}")
            print(f"  Split:   {split}")
            print("=" * 60)
            print("  Would run in-process via TEND.run_tend.run_tend_split")
        print("\n" + "=" * 60)
        print(f"  Dry run complete — {total} run(s) planned, none executed.")
        print("=" * 60)
        return 0

    evaluator: QwenTENDEvaluator | None = None
    doc_generator: QwenDocumentationGenerator | None = None
    if evaluate or generate_documentation:
        print(f"\nLoading Qwen model once: {model_name}")
        evaluator = QwenTENDEvaluator(model_name=model_name)
        evaluator.load()
        if generate_documentation:
            doc_generator = QwenDocumentationGenerator(
                model_name=model_name,
                evaluator=evaluator,
            )
        print("Model loaded and ready.")

    print("\nLoading Spider tables once ...")
    spider_source = SpiderSource()
    tables_by_db = spider_source.load_tables()
    translator = SQLToNoSQLTranslator()
    print(f"Loaded {len(tables_by_db)} database schemas.")

    failures: list[str] = []

    for split in splits:
        print("\n" + "=" * 60)
        print(f"  Dataset: {args.dataset}")
        print(f"  Split:   {split}")
        print("=" * 60)
        try:
            run_tend_split(
                dataset=args.dataset,
                split=split,
                max_samples=args.max_samples,
                evaluate=evaluate,
                generate_documentation=generate_documentation,
                model_name=model_name,
                evaluator=evaluator,
                doc_generator=doc_generator,
                spider_source=spider_source,
                tables_by_db=tables_by_db,
                translator=translator,
            )
        except Exception as exc:
            failures.append(f"{args.dataset} / {split} ({exc})")
            print(f"ERROR: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print(f"  Finished with {len(failures)} failure(s):")
        for item in failures:
            print(f"    - {item}")
    else:
        print(f"  All {total} run(s) completed successfully.")
    print("=" * 60)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
