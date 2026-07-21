#!/usr/bin/env python3
"""CLI entry point mirroring notebooks/01_checkpoint1_foundation_and_docgen.ipynb.

Lets Checkpoint 1 be reproduced outside Colab (e.g. on a lab GPU box or in CI
with mocked models) via:

    python scripts/run_checkpoint1_eval.py --eval-n 100

All behavior is driven by configs/*.yaml — no hardcoded paths or magic numbers
live in this script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from codegen_rag.data.downloaders import download_all  # noqa: E402
from codegen_rag.data.preprocessors import (  # noqa: E402
    parse_codocbench_directory,
    train_val_test_split,
)
from codegen_rag.evaluation.evaluator import Evaluator  # noqa: E402
from codegen_rag.models.codegen_wrapper import load_model_for_task  # noqa: E402
from codegen_rag.models.generation_config import GenerationConfig  # noqa: E402
from codegen_rag.tasks.code_translation import CodeTranslationTask  # noqa: E402
from codegen_rag.tasks.commit_message_generation import CommitMessageGenerationTask  # noqa: E402
from codegen_rag.tasks.documentation_generation import DocumentationGenerationTask  # noqa: E402
from codegen_rag.tasks.program_synthesis import ProgramSynthesisTask  # noqa: E402
from codegen_rag.utils.env_setup import bootstrap_environment  # noqa: E402
from codegen_rag.utils.io_utils import write_jsonl  # noqa: E402
from codegen_rag.utils.logging_config import get_logger  # noqa: E402

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Checkpoint 1 baseline evaluation")
    parser.add_argument("--eval-n", type=int, default=100, help="Number of test records to evaluate per task")
    parser.add_argument("--skip-download", action="store_true", help="Skip dataset download step")
    parser.add_argument("--install-deps", action="store_true", help="Install requirements.txt before running")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = bootstrap_environment(install_deps=args.install_deps, mount_drive=False)

    if not args.skip_download:
        download_all(settings)

    codoc_cfg = settings.data["codocbench"]
    codoc_root = settings.resolve_path(codoc_cfg["clone_dir"])
    records = parse_codocbench_directory(codoc_root, languages=codoc_cfg["languages"])
    record_dicts = [r.to_dict() for r in records]
    splits = train_val_test_split(
        record_dicts,
        train_ratio=codoc_cfg["split_ratios"]["train"],
        val_ratio=codoc_cfg["split_ratios"]["val"],
        seed=settings.project.seed,
    )
    for split_name, split_records in splits.items():
        write_jsonl(split_records, settings.path_for("data_processed") / f"codocbench_{split_name}.jsonl")

    eval_records = splits["test"][: args.eval_n]
    model = load_model_for_task(settings)
    gen_cfg = settings.model["generation"]
    evaluator = Evaluator(settings.path_for("results"))

    tasks = [
        ProgramSynthesisTask(model, GenerationConfig(**gen_cfg["program_synthesis"])),
        DocumentationGenerationTask(model, GenerationConfig(**gen_cfg["documentation_generation"])),
        CodeTranslationTask(model, GenerationConfig(**gen_cfg["code_translation"])),
    ]
    summaries = [evaluator.evaluate_task(t, eval_records, model_tier="small_lm_baseline") for t in tasks]

    commit_records = [r for r in eval_records if r.get("commit_diff") and r.get("commit_message")]
    if commit_records:
        commit_task = CommitMessageGenerationTask(model, GenerationConfig(**gen_cfg["commit_message_generation"]))
        summaries.append(evaluator.evaluate_task(commit_task, commit_records, model_tier="small_lm_baseline"))

    df = evaluator.build_comparison_table(summaries)
    logger.info("Checkpoint 1 evaluation complete:\n%s", df.to_string())


if __name__ == "__main__":
    main()
