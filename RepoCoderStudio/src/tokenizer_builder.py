"""
============================================================
RepoCoder Studio
tokenizer_builder.py  —  v2.5
============================================================

Hugging Face Dataset preparation with task-aware curriculum ordering.

Public API retained
-------------------
TokenizerDatasetBuilder(CONFIG).build(task_examples) -> train, validation, test
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from datasets import Dataset

from src.config import CONFIG, AppConfig
from src.schemas import TaskExample
from src.logger import SectionPrinter, SummaryPrinter
from src.curriculum_builder import CurriculumBuilder


class TokenizerDatasetBuilder:
    """Builds HF train/validation/test datasets from TaskExample objects."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.curriculum = CurriculumBuilder(config)

    def task_examples_to_rows(self, task_examples: List[TaskExample]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for ex in task_examples:
            metadata = dict(ex.metadata or {})
            rows.append({
                "task_id": ex.task_id,
                "corpus_id": ex.corpus_id,
                "source_modality": ex.source_modality,
                "target_modality": ex.target_modality,
                "split": ex.split,
                "instruction": ex.instruction,
                "input_text": ex.input_text,
                "output_text": ex.output_text,
                "text": metadata.get("training_text", ""),
                "prompt_version": metadata.get("prompt_version"),
                "task_contract_version": metadata.get("task_contract_version"),
                "task_family": metadata.get("task_family"),
                "curriculum_stage": metadata.get("curriculum_stage"),
                "difficulty": metadata.get("difficulty"),
                "expected_output_kind": metadata.get("expected_output_kind"),
                "prompt_task_token": metadata.get("prompt_task_token"),
                "output_contract": metadata.get("output_contract"),
                "csr_score": metadata.get("csr_score"),
                "alignment_strategy": metadata.get("alignment_strategy"),
                "teacher_generated_or_repaired": metadata.get("teacher_generated_or_repaired"),
                "trusted_test_status": metadata.get("trusted_test_status"),
            })
        return rows

    def split_rows(self, rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        train_rows = [r for r in rows if r.get("split") == "train"]
        validation_rows = [r for r in rows if r.get("split") in {"validation", "valid", "dev"}]
        test_rows = [r for r in rows if r.get("split") == "test"]
        return train_rows, validation_rows, test_rows

    def _task_counts(self, rows: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for r in rows:
            task_id = str(r.get("task_id", "unknown"))
            counts[task_id] = counts.get(task_id, 0) + 1
        return dict(sorted(counts.items()))

    def _dataset_from_rows(self, rows: List[Dict[str, Any]]) -> Dataset:
        return Dataset.from_list(rows) if rows else Dataset.from_list([])

    def build(self, task_examples: List[TaskExample]):
        SectionPrinter.header("Tokenizer Dataset Builder  [v2.5]")
        rows = self.task_examples_to_rows(task_examples)
        train_rows, validation_rows, test_rows = self.split_rows(rows)

        train_rows = self.curriculum.apply(train_rows, split_name="train")
        validation_rows = self.curriculum.apply(validation_rows, split_name="validation")
        test_rows = self.curriculum.apply(test_rows, split_name="test")

        train_ds = self._dataset_from_rows(train_rows)
        validation_ds = self._dataset_from_rows(validation_rows)
        test_ds = self._dataset_from_rows(test_rows)

        SummaryPrinter.print_summary(
            "HF Dataset Summary  [v2.5]",
            {
                "Train Rows": len(train_ds),
                "Validation Rows": len(validation_ds),
                "Test Rows": len(test_ds),
                "Train Task Counts": self._task_counts(train_rows),
                "Validation Task Counts": self._task_counts(validation_rows),
                "Test Task Counts": self._task_counts(test_rows),
                "Curriculum": "round_robin_by_task",
            },
        )
        return train_ds, validation_ds, test_ds
