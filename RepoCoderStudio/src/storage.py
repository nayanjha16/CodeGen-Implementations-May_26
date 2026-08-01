"""
============================================================
RepoCoder Studio
storage.py
============================================================

Google Drive Project Storage Manager.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter


class ProjectStorageManager:
    """
    Central storage manager for RepoCoder Studio.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.root = Path(config.storage.drive_project_root)

    def initialize_project(self):
        SectionPrinter.header("Project Folder Initialization")

        folders = [
            self.config.storage.notebooks_dir,
            self.config.storage.src_dir,
            self.config.storage.configs_dir,
            self.config.storage.datasets_dir,
            "datasets/xlcost",
            "datasets/xlcost/python",
            "datasets/xlcost/java",
            "datasets/codexglue/python",
            "datasets/codexglue/java",
            self.config.storage.outputs_dir,
            self.config.storage.candidate_corpus_dir,
            self.config.storage.approved_corpus_dir,
            self.config.storage.rejected_corpus_dir,
            self.config.storage.trusted_tests_dir,
            self.config.storage.task_datasets_dir,
            self.config.storage.checkpoints_dir,
            self.config.storage.adapters_dir,
            self.config.storage.evaluation_dir,
            self.config.storage.reports_dir,
            self.config.storage.logs_dir,
            self.config.storage.manifests_dir,
            self.config.storage.repo_explorer_output_dir,
            self.config.storage.repo_explorer_embedding_dir,
            self.config.storage.corpus_index_dir,
            "tests",
        ]

        created = 0
        existing = 0

        for folder in folders:
            path = self.root / folder
            if path.exists():
                existing += 1
            else:
                path.mkdir(parents=True, exist_ok=True)
                created += 1

        SummaryPrinter.print_summary(
            "Storage Initialization Summary",
            {
                "Project Root": str(self.root),
                "Folders Created": created,
                "Folders Already Existing": existing,
            },
        )

    def path(self, relative_path: str) -> Path:
        return self.root / relative_path

    def ensure_parent(self, file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self, relative_path: str) -> bool:
        return self.path(relative_path).exists()

    def should_resume(self, relative_path: str) -> bool:
        return (
            self.config.runtime.auto_resume
            and not self.config.runtime.overwrite_existing
            and self.exists(relative_path)
        )

    def save_json(self, data: Dict[str, Any], relative_path: str):
        file_path = self.path(relative_path)
        self.ensure_parent(file_path)

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        LOG.info(f"Saved JSON: {file_path}")

    def load_json(self, relative_path: str) -> Dict[str, Any]:
        file_path = self.path(relative_path)
        assert file_path.exists(), f"JSON file not found: {file_path}"

        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_jsonl(self, rows: List[Dict[str, Any]], relative_path: str):
        file_path = self.path(relative_path)
        self.ensure_parent(file_path)

        with file_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        LOG.info(f"Saved JSONL: {file_path} ({len(rows)} rows)")

    def load_jsonl(self, relative_path: str) -> List[Dict[str, Any]]:
        file_path = self.path(relative_path)
        assert file_path.exists(), f"JSONL file not found: {file_path}"

        rows = []
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))

        LOG.info(f"Loaded JSONL: {file_path} ({len(rows)} rows)")
        return rows

    def append_jsonl(self, row: Dict[str, Any], relative_path: str):
        """Appends a single row to a JSONL file, creating it if needed.

        Used for logs that accumulate one event at a time (e.g. Stage 5's
        retrieval query log) rather than being written once from a
        fully-built in-memory list like save_jsonl's other callers.
        """
        file_path = self.path(relative_path)
        self.ensure_parent(file_path)

        with file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        LOG.debug(f"Appended JSONL row: {file_path}")

    def save_csv(self, df: pd.DataFrame, relative_path: str):
        file_path = self.path(relative_path)
        self.ensure_parent(file_path)
        df.to_csv(file_path, index=False)
        LOG.info(f"Saved CSV: {file_path} ({len(df)} rows)")

    def load_csv(self, relative_path: str) -> pd.DataFrame:
        file_path = self.path(relative_path)
        assert file_path.exists(), f"CSV file not found: {file_path}"
        df = pd.read_csv(file_path)
        LOG.info(f"Loaded CSV: {file_path} ({len(df)} rows)")
        return df

    def save_text(self, text: str, relative_path: str):
        file_path = self.path(relative_path)
        self.ensure_parent(file_path)
        file_path.write_text(text, encoding="utf-8")
        LOG.info(f"Saved text: {file_path}")

    def load_text(self, relative_path: str) -> str:
        file_path = self.path(relative_path)
        assert file_path.exists(), f"Text file not found: {file_path}"
        return file_path.read_text(encoding="utf-8")

    def save_run_manifest(self, manifest: Dict[str, Any]):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        relative_path = (
            f"{self.config.storage.manifests_dir}/"
            f"run_manifest_{timestamp}.json"
        )
        self.save_json(manifest, relative_path)

    def save_config_snapshot(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        relative_path = (
            f"{self.config.storage.manifests_dir}/"
            f"config_snapshot_{timestamp}.json"
        )
        self.save_json(self.config.to_dict(), relative_path)

    def candidate_corpus_path(self) -> str:
        return f"{self.config.storage.candidate_corpus_dir}/candidate_corpus.jsonl"

    def duplicate_report_path(self) -> str:
        return f"{self.config.storage.candidate_corpus_dir}/duplicate_report.jsonl"

    def approved_corpus_path(self) -> str:
        return f"{self.config.storage.approved_corpus_dir}/approved_corpus.jsonl"

    def rejected_corpus_path(self) -> str:
        return f"{self.config.storage.rejected_corpus_dir}/rejected_corpus.jsonl"

    def task_dataset_path(self) -> str:
        return f"{self.config.storage.task_datasets_dir}/task_dataset.jsonl"

    # ------------------------------------------------------------
    # Stage 4/5 -- repository understanding + RAG
    # ------------------------------------------------------------

    def repo_explorer_output_dir(self) -> Path:
        """Absolute dir for Step 1/3 build artifacts (repo_index.json,
        FAISS indices) -- RepositoryExplorer writes/reads these directly,
        the same way trainer.py writes adapter weights directly rather
        than through save_json (binary/non-JSON artifacts)."""
        return self.path(self.config.storage.repo_explorer_output_dir)

    def repo_explorer_embedding_dir(self) -> Path:
        """Absolute dir for Step 2 embedding .npy/.json artifacts."""
        return self.path(self.config.storage.repo_explorer_embedding_dir)

    def repo_explorer_report_path(self) -> str:
        return f"{self.config.storage.reports_dir}/repo_explorer_summary.json"

    def repo_explorer_eval_path(self) -> str:
        return f"{self.config.storage.reports_dir}/repo_explorer_eval_metrics.json"

    def retrieval_query_log_path(self) -> str:
        return f"{self.config.storage.reports_dir}/retrieval_query_log.jsonl"

    def corpus_index_dir(self) -> Path:
        """Absolute dir for the Stage 5 corpus-retrieval FAISS index built
        directly over approved_corpus.jsonl (see src/corpus_retriever.py)."""
        return self.path(self.config.storage.corpus_index_dir)

    def corpus_index_report_path(self) -> str:
        return f"{self.config.storage.reports_dir}/corpus_index_summary.json"

    def repobench_eval_report_path(self, language: str = "python") -> str:
        return f"{self.config.storage.reports_dir}/repobench_eval_summary_{language}.json"

    def swebench_localization_report_path(self) -> str:
        return f"{self.config.storage.reports_dir}/swebench_localization_summary.json"

    def realworld_generation_eval_report_path(self, language: str = "python") -> str:
        return f"{self.config.storage.reports_dir}/realworld_generation_eval_summary_{language}.json"

    def print_project_status(self):
        SectionPrinter.header("Project Artifact Status")

        checks = {
            "Candidate Corpus": self.candidate_corpus_path(),
            "Duplicate Report": self.duplicate_report_path(),
            "Approved Corpus": self.approved_corpus_path(),
            "Rejected Corpus": self.rejected_corpus_path(),
            "Task Dataset": self.task_dataset_path(),
            "Checkpoints Folder": self.config.storage.checkpoints_dir,
            "Adapters Folder": self.config.storage.adapters_dir,
            "Repo Explorer Report (Stage 4)": self.repo_explorer_report_path(),
            "Retrieval Query Log (Stage 5)": self.retrieval_query_log_path(),
            "Corpus Index Report (Stage 5)": self.corpus_index_report_path(),
        }

        for label, rel_path in checks.items():
            status = "FOUND" if self.exists(rel_path) else "MISSING"
            print(f"{label:<24}: {status}")

        print("=" * 68)
