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
        }

        for label, rel_path in checks.items():
            status = "FOUND" if self.exists(rel_path) else "MISSING"
            print(f"{label:<24}: {status}")

        print("=" * 68)
