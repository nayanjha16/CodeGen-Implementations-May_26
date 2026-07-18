"""
============================================================
RepoCoder Studio
task_builder.py  —  v2.3
============================================================

Task Dataset Builder.

Purpose
-------
Expands ApprovedCorpus rows into the six supervised tasks defined by the
RepoCoder Studio Combined Stage specification.

Design position
---------------
The Task Builder is intentionally corpus-driven. It never reads raw datasets
and never applies dataset-specific task logic. Every TaskExample is derived from
an ApprovedRow that already contains the complete NL + Python + Java triple.

v2.1 updates
------------
- Keeps the existing public API: TaskDatasetBuilder(CONFIG).build(approved_rows)
- Adds task-contract metadata for downstream prompt/curriculum/training logic.
- Adds difficulty estimation from stored AST / parse-tree artifacts.
- Adds curriculum-stage metadata without changing downstream dataclasses.
- Preserves training_text inside metadata for backward compatibility.
- Writes task distribution artifacts for report/debugging.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import pandas as pd

from src.config import CONFIG, AppConfig
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.prompt_builder import PromptBuilder
from src.registry import TaskRegistry
from src.schemas import ApprovedRow, TaskExample, dataclass_to_dict
from src.storage import ProjectStorageManager


# ============================================================
# Constants
# ============================================================

TASK_BUILDER_VERSION = "task_builder_v2.3"
TASK_CONTRACT_VERSION = "task_contract_v2.6"
PROMPT_VERSION = "prompt_contract_v2.6"


_TASK_FAMILY = {
    "T1": "nl_to_code",
    "T2": "nl_to_code",
    "T3": "code_translation",
    "T4": "code_translation",
    "T5": "code_to_nl",
    "T6": "code_to_nl",
}

# Curriculum stage is metadata only at this layer. Actual sampling/order is
# handled later by CurriculumBuilder / TokenizerDatasetBuilder.
_CURRICULUM_STAGE = {
    "T1": 1,
    "T2": 1,
    "T3": 2,
    "T4": 2,
    "T5": 3,
    "T6": 3,
}

_EXPECTED_OUTPUT_KIND = {
    "T1": "python_code",
    "T2": "java_code",
    "T3": "java_code",
    "T4": "python_code",
    "T5": "natural_language",
    "T6": "natural_language",
}


# ============================================================
# Utility helpers
# ============================================================

def _safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Reads a field from either a dataclass/object or a dictionary."""
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {} if value is None else dict(value) if isinstance(value, Mapping) else {}


def _text_len_lines(text: str) -> int:
    if not text:
        return 0
    return len([line for line in str(text).splitlines() if line.strip()])


def _bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


# ============================================================
# Task Dataset Builder
# ============================================================

class TaskDatasetBuilder:
    """
    Converts ApprovedRow objects into TaskExample objects.

    One approved row generates six supervised tasks:

    T1  Natural Language -> Python
    T2  Natural Language -> Java
    T3  Python -> Java
    T4  Java -> Python
    T5  Python -> Natural Language
    T6  Java -> Natural Language

    This builder does not perform prompt-tokenization or curriculum sampling.
    It creates task examples and attaches the metadata required by those later
    pipeline stages.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.task_registry = TaskRegistry()
        self.prompt_builder = PromptBuilder()

    # --------------------------------------------------------
    # Task IO mapping
    # --------------------------------------------------------

    def _get_input_output(self, row: ApprovedRow, task_id: str) -> Tuple[str, str]:
        """Returns input/output text for one task."""

        natural_language = _safe_get(row, "natural_language", "") or ""
        python_code = _safe_get(row, "python_code", "") or ""
        java_code = _safe_get(row, "java_code", "") or ""

        if task_id == "T1":
            return natural_language, python_code

        if task_id == "T2":
            return natural_language, java_code

        if task_id == "T3":
            return python_code, java_code

        if task_id == "T4":
            return java_code, python_code

        if task_id == "T5":
            return python_code, natural_language

        if task_id == "T6":
            return java_code, natural_language

        raise ValueError(f"Unknown task_id: {task_id}")

    # --------------------------------------------------------
    # Metadata extraction
    # --------------------------------------------------------

    def _estimate_difficulty(self, row: ApprovedRow) -> str:
        """
        Estimates example difficulty from approved parser artifacts.

        The goal is not to grade the programming problem perfectly. The goal is
        to provide a stable curriculum hint that downstream sampling can use.
        """

        python_ast = _as_dict(_safe_get(row, "python_ast", {}))
        java_tree = _as_dict(_safe_get(row, "java_parse_tree", {}))

        py_nodes = int(python_ast.get("ast_node_count") or 0)
        java_nodes = int(java_tree.get("parse_tree_node_count") or 0)
        py_lines = int(python_ast.get("line_count") or _text_len_lines(_safe_get(row, "python_code", "")))
        java_methods = int(java_tree.get("method_count") or 0)

        complexity_score = 0
        complexity_score += min(py_nodes / 80.0, 3.0)
        complexity_score += min(java_nodes / 200.0, 3.0)
        complexity_score += min(py_lines / 20.0, 2.0)
        complexity_score += min(java_methods / 3.0, 2.0)
        complexity_score += _bool_int(python_ast.get("has_loop") or java_tree.get("has_loop"))
        complexity_score += _bool_int(python_ast.get("has_conditional") or java_tree.get("has_conditional"))
        complexity_score += _bool_int(python_ast.get("has_recursion"))

        if complexity_score < 4.0:
            return "easy"
        if complexity_score < 7.5:
            return "medium"
        return "hard"

    def _teacher_metadata(self, row: ApprovedRow) -> Dict[str, Any]:
        """Extracts teacher/repair provenance without assuming a fixed schema."""

        repair_history = _safe_get(row, "repair_history", []) or []
        metadata = _as_dict(_safe_get(row, "metadata", {}))
        provenance = _as_dict(_safe_get(row, "provenance", {}))

        teacher_keys = [
            key for key in list(metadata.keys()) + list(provenance.keys())
            if "teacher" in str(key).lower() or "repair" in str(key).lower()
        ]

        teacher_generated = bool(repair_history or teacher_keys)
        successful_attempts = []

        for item in repair_history:
            if not isinstance(item, Mapping):
                continue
            status = str(item.get("status", item.get("outcome", ""))).upper()
            if status in {"PASS", "SUCCESS", "APPROVED", "VALID"}:
                successful_attempts.append(item.get("attempt"))

        return {
            "teacher_generated_or_repaired": teacher_generated,
            "repair_attempt_count": len(repair_history),
            "teacher_success_attempt": successful_attempts[0] if successful_attempts else None,
            "repair_history_present": bool(repair_history),
            "teacher_or_repair_keys": sorted(set(map(str, teacher_keys)))[:20],
        }

    def _task_metadata(
        self,
        row: ApprovedRow,
        task_id: str,
        task_info: Dict[str, Any],
        instruction: str,
        input_text: str,
        output_text: str,
    ) -> Dict[str, Any]:
        """Builds versioned task metadata consumed by Batch 3 modules."""

        row_metadata = _as_dict(_safe_get(row, "metadata", {}))
        provenance = _as_dict(_safe_get(row, "provenance", {}))
        semantic_artifacts = _as_dict(_safe_get(row, "semantic_artifacts", {}))

        corpus_id = _safe_get(row, "corpus_id", "")
        csr_score = _safe_get(row, "csr_score", None)
        if csr_score is None:
            csr_score = row_metadata.get("csr_score", row_metadata.get("csr_similarity"))

        prompt_profile = {}
        try:
            prompt_profile = self.prompt_builder.task_profile(task_id)
        except Exception:
            prompt_profile = {}

        training_text = self.prompt_builder.build_training_text(
            instruction,
            input_text,
            output_text,
            task_id=task_id,
        )
        prompt_hash = self.prompt_builder.prompt_hash(training_text)
        response_header = prompt_profile.get("response_header", "### Response")
        success_criteria = prompt_profile.get("success_criteria", [])

        teacher_meta = self._teacher_metadata(row)

        return {
            # Backward-compatible fields
            "dataset": provenance.get("dataset") or row_metadata.get("dataset"),
            "csr_similarity": csr_score,
            "csr_score": csr_score,
            "training_text": training_text,
            "prompt_hash": prompt_hash,
            "response_header": response_header,

            # v2.3 task contract metadata
            "task_builder_version": TASK_BUILDER_VERSION,
            "task_contract_version": TASK_CONTRACT_VERSION,
            "prompt_version": PROMPT_VERSION,
            "task_id": task_id,
            "task_family": _TASK_FAMILY.get(task_id, "unknown"),
            "curriculum_stage": _CURRICULUM_STAGE.get(task_id, 99),
            "difficulty": self._estimate_difficulty(row),
            "expected_output_kind": _EXPECTED_OUTPUT_KIND.get(task_id, "unknown"),
            "source_modality": task_info.get("source"),
            "target_modality": task_info.get("target"),
            "prompt_label": prompt_profile.get("label"),
            "prompt_task_token": prompt_profile.get("task_token"),
            "output_contract": prompt_profile.get("output_contract") or prompt_profile.get("contract"),
            "prompt_constraints": prompt_profile.get("constraints", []),
            "prompt_quality_checks": prompt_profile.get("quality_checks", []),
            "prompt_success_criteria": success_criteria,
            "prompt_forbidden_outputs": prompt_profile.get("forbidden_outputs", []),
            "prompt_stop_sequences": prompt_profile.get("stop_sequences", []),

            # Corpus/provenance metadata
            "corpus_id": corpus_id,
            "corpus_version": _safe_get(row, "corpus_version", provenance.get("corpus_version")),
            "split": provenance.get("split", _safe_get(row, "split", "unknown")),
            "alignment_strategy": row_metadata.get("alignment_strategy"),
            "alignment_confidence": row_metadata.get("alignment_confidence"),
            "validation_status": _safe_get(row, "validation_status", None),
            "validation_version": row_metadata.get("validation_version") or row_metadata.get("normalizer_version"),
            "execution_status": row_metadata.get("execution_status"),
            "trusted_test_status": _as_dict(_safe_get(row, "trusted_tests", {})).get("status"),

            # Structural hints for curriculum/evaluation
            "python_ast_node_count": _as_dict(_safe_get(row, "python_ast", {})).get("ast_node_count"),
            "java_parse_tree_node_count": _as_dict(_safe_get(row, "java_parse_tree", {})).get("parse_tree_node_count"),
            "python_line_count": _as_dict(_safe_get(row, "python_ast", {})).get("line_count"),
            "java_method_count": _as_dict(_safe_get(row, "java_parse_tree", {})).get("method_count"),
            "semantic_artifact_keys": sorted(list(semantic_artifacts.keys())),

            # Teacher/repair metadata
            **teacher_meta,
        }

    # --------------------------------------------------------
    # Main public API
    # --------------------------------------------------------

    def build(self, approved_rows: List[ApprovedRow]) -> List[TaskExample]:
        """Builds the task-expanded dataset and persists it to JSONL."""

        SectionPrinter.header("Task Dataset Builder  [v2.3]")

        task_examples: List[TaskExample] = []
        skipped = 0

        for row in approved_rows:
            split = _as_dict(_safe_get(row, "provenance", {})).get("split", "unknown")
            corpus_id = _safe_get(row, "corpus_id", "")

            for task_id, task_info in self.task_registry.all_tasks().items():
                input_text, output_text = self._get_input_output(row, task_id)

                if not str(input_text).strip() or not str(output_text).strip():
                    skipped += 1
                    continue

                instruction = self.prompt_builder.build_instruction(task_id)
                metadata = self._task_metadata(
                    row=row,
                    task_id=task_id,
                    task_info=task_info,
                    instruction=instruction,
                    input_text=input_text,
                    output_text=output_text,
                )

                task_examples.append(
                    TaskExample(
                        task_id=task_id,
                        corpus_id=corpus_id,
                        source_modality=task_info["source"],
                        target_modality=task_info["target"],
                        instruction=instruction,
                        input_text=input_text,
                        output_text=output_text,
                        split=split,
                        metadata=metadata,
                    )
                )

        rows = [dataclass_to_dict(row) for row in task_examples]
        self.storage.save_jsonl(rows, self.storage.task_dataset_path())
        self._write_task_reports(task_examples, skipped=skipped, approved_count=len(approved_rows))

        SummaryPrinter.print_summary(
            "Task Dataset Summary  [v2.3]",
            {
                "Approved Rows": len(approved_rows),
                "Task Examples": len(task_examples),
                "Expected Max": len(approved_rows) * 6,
                "Skipped Empty Tasks": skipped,
                "Prompt Version": PROMPT_VERSION,
            },
        )

        return task_examples

    # --------------------------------------------------------
    # Reporting helpers
    # --------------------------------------------------------

    def split_summary(self, task_examples: List[TaskExample]) -> Dict[str, int]:
        """Counts task examples by split."""
        return dict(Counter(row.split for row in task_examples))

    def task_summary(self, task_examples: List[TaskExample]) -> Dict[str, int]:
        """Counts task examples by task ID."""
        return dict(Counter(row.task_id for row in task_examples))

    def task_split_summary(self, task_examples: List[TaskExample]) -> Dict[str, Dict[str, int]]:
        """Counts task examples by task and split."""
        counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for row in task_examples:
            counts[row.task_id][row.split] += 1
        return {task: dict(split_counts) for task, split_counts in counts.items()}

    def _write_task_reports(self, task_examples: List[TaskExample], skipped: int, approved_count: int) -> None:
        """Persists task-distribution reports used by the notebook and report."""

        if not task_examples:
            return

        rows = [dataclass_to_dict(row) for row in task_examples]
        flat_rows = []
        for row in rows:
            metadata = row.get("metadata", {}) or {}
            flat_rows.append(
                {
                    "task_id": row.get("task_id"),
                    "split": row.get("split"),
                    "source_modality": row.get("source_modality"),
                    "target_modality": row.get("target_modality"),
                    "dataset": metadata.get("dataset"),
                    "task_family": metadata.get("task_family"),
                    "difficulty": metadata.get("difficulty"),
                    "curriculum_stage": metadata.get("curriculum_stage"),
                    "prompt_version": metadata.get("prompt_version"),
                    "prompt_hash": metadata.get("prompt_hash"),
                    "response_header": metadata.get("response_header"),
                    "teacher_generated_or_repaired": metadata.get("teacher_generated_or_repaired"),
                    "alignment_strategy": metadata.get("alignment_strategy"),
                }
            )

        df = pd.DataFrame(flat_rows)

        try:
            task_dist = (
                df.groupby(["task_id", "source_modality", "target_modality", "split"])
                .size()
                .reset_index(name="count")
                .sort_values(["task_id", "split"])
            )
            self.storage.save_csv(task_dist, "outputs/reports/task_distribution_v2_3.csv")

            family_dist = (
                df.groupby(["task_family", "task_id", "difficulty"])
                .size()
                .reset_index(name="count")
                .sort_values(["task_family", "task_id", "difficulty"])
            )
            self.storage.save_csv(family_dist, "outputs/reports/task_family_difficulty_v2_3.csv")

            dataset_dist = (
                df.groupby(["dataset", "task_id"])
                .size()
                .reset_index(name="count")
                .sort_values(["dataset", "task_id"])
            )
            self.storage.save_csv(dataset_dist, "outputs/reports/task_dataset_contribution_v2_3.csv")

            summary = {
                "task_builder_version": TASK_BUILDER_VERSION,
                "task_contract_version": TASK_CONTRACT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "approved_rows": approved_count,
                "task_examples": len(task_examples),
                "expected_max": approved_count * 6,
                "skipped_empty_tasks": skipped,
                "by_task": self.task_summary(task_examples),
                "by_split": self.split_summary(task_examples),
                "by_task_split": self.task_split_summary(task_examples),
            }
            self.storage.save_json(summary, "outputs/reports/task_dataset_summary_v2_3.json")

        except Exception as exc:
            LOG.warning(f"Could not write task reports: {exc}")
