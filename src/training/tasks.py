"""Training task definitions for LoRA fine-tuning."""

from __future__ import annotations

from enum import Enum

TRAINING_TASKS = frozenset({"text2sql", "sql2nosql", "nosql2doc"})


class TaskType(str, Enum):
    """Supported fine-tuning tasks."""

    TEXT2SQL = "text2sql"
    SQL2NOSQL = "sql2nosql"
    NOSQL2DOC = "nosql2doc"

    @classmethod
    def from_str(cls, value: str) -> "TaskType":
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            allowed = ", ".join(sorted(TRAINING_TASKS))
            raise ValueError(
                f"Unknown training task '{value}'. Expected one of: {allowed}"
            ) from exc
