"""
RepoCoder Studio — offline training pipeline CLI.

Runs the same sequence of stages as the notebook's Combined Stage cells
(dataset load -> candidate corpus -> validation -> task dataset -> tokenizer
dataset -> LoRA training), using the unmodified src/*.py modules. Produces a
real trained LoRA adapter under outputs/adapters/<final_adapter_name>/ that
the FastAPI inference app (app/main.py) reads on startup.

Intended to run once inside the training Docker image (Dockerfile.train), not
as part of the deployed inference container.
"""

import shutil

from src.config import CONFIG
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.storage import ProjectStorageManager
from src.dataset_loader import DatasetLoader
from src.corpus_builder import CandidateCorpusBuilder
from src.validation_engine import ValidationEngine
from src.task_builder import TaskDatasetBuilder
from src.tokenizer_builder import TokenizerDatasetBuilder
from src.trainer import RepoCoderTrainer


def clean_stale_artifacts(storage: ProjectStorageManager) -> None:
    SectionPrinter.header("Cleaning Stale Artifacts")

    stale_relative_paths = [
        storage.candidate_corpus_path(),
        storage.duplicate_report_path(),
        storage.approved_corpus_path(),
        storage.rejected_corpus_path(),
        f"{CONFIG.storage.reports_dir}/validation_report.jsonl",
        f"{CONFIG.storage.task_datasets_dir}/task_dataset.jsonl",
        "outputs/reports/alignment_analytics.jsonl",
        "outputs/teacher_queue/teacher_completion_queue.jsonl",
    ]

    for relative_path in stale_relative_paths:
        path = storage.path(relative_path)
        if path.exists():
            path.unlink()
            LOG.info(f"Deleted stale artifact: {path}")

    adapter_dir = (
        CONFIG.storage.project_root()
        / CONFIG.storage.adapters_dir
        / CONFIG.training.final_adapter_name
    )
    if adapter_dir.exists():
        shutil.rmtree(adapter_dir)
        LOG.info(f"Deleted stale adapter directory: {adapter_dir}")


def main() -> None:
    storage = ProjectStorageManager(CONFIG)
    storage.initialize_project()

    clean_stale_artifacts(storage)

    SectionPrinter.header("Stage 1/6 — Load Raw Datasets")
    loader = DatasetLoader(CONFIG)
    raw_datasets = loader.load_all()

    SectionPrinter.header("Stage 2/6 — Build Candidate Corpus")
    candidate_builder = CandidateCorpusBuilder(CONFIG)
    candidate_rows = candidate_builder.build(raw_datasets)
    LOG.info(f"Candidate rows: {len(candidate_rows)}")

    SectionPrinter.header("Stage 3/6 — Validate Corpus")
    validation_engine = ValidationEngine(CONFIG)
    approved_rows, rejected_rows, _validation_reports = validation_engine.run(candidate_rows)
    LOG.info(f"Approved rows: {len(approved_rows)} | Rejected rows: {len(rejected_rows)}")

    if not approved_rows:
        raise RuntimeError(
            "No approved rows survived validation — cannot build a task dataset "
            "or train. Check the validation report for rejection reasons."
        )

    SectionPrinter.header("Stage 4/6 — Build Task Dataset")
    task_builder = TaskDatasetBuilder(CONFIG)
    task_examples = task_builder.build(approved_rows)
    LOG.info(f"Task examples: {len(task_examples)}")

    SectionPrinter.header("Stage 5/6 — Build Tokenizer Datasets")
    tokenizer_builder = TokenizerDatasetBuilder(CONFIG)
    train_dataset, validation_dataset, test_dataset = tokenizer_builder.build(task_examples)
    LOG.info(
        f"Train rows: {len(train_dataset)} | "
        f"Validation rows: {len(validation_dataset)} | "
        f"Test rows: {len(test_dataset)}"
    )

    SectionPrinter.header("Stage 6/6 — LoRA Training")
    repocoder_trainer = RepoCoderTrainer(CONFIG)
    repocoder_trainer.train(
        train_dataset=train_dataset,
        validation_dataset=validation_dataset,
    )

    adapter_dir = (
        CONFIG.storage.project_root()
        / CONFIG.storage.adapters_dir
        / CONFIG.training.final_adapter_name
    )

    SummaryPrinter.print_summary(
        "Training Pipeline Complete",
        {
            "Candidate Rows": len(candidate_rows),
            "Approved Rows": len(approved_rows),
            "Rejected Rows": len(rejected_rows),
            "Task Examples": len(task_examples),
            "Train Rows": len(train_dataset),
            "Validation Rows": len(validation_dataset),
            "Test Rows": len(test_dataset),
            "Final Adapter Directory": str(adapter_dir),
        },
    )


if __name__ == "__main__":
    main()
