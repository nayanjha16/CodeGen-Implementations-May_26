"""Training task definitions for LoRA fine-tuning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

TRAINING_TASKS = frozenset({"text2sql", "sql2nosql", "nosql2doc"})
DEFAULT_TRAINING_CONFIGS = ("spider", "bird")
DEFAULT_TRAINING_SPLIT = "train"
DEFAULT_EVAL_CONFIGS = ("spider", "bird")
DEFAULT_EVAL_SPLIT = "test"


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


@dataclass(frozen=True)
class TaskSpec:
    """Column wiring and collator hints for one training task."""

    task: TaskType
    required_fields: tuple[str, ...]
    target_field: str
    response_template: str


TASK_SPECS: dict[str, TaskSpec] = {
    TaskType.TEXT2SQL.value: TaskSpec(
        task=TaskType.TEXT2SQL,
        required_fields=("question", "schema", "sql"),
        target_field="sql",
        response_template="\n\nSQL:",
    ),
    TaskType.SQL2NOSQL.value: TaskSpec(
        task=TaskType.SQL2NOSQL,
        required_fields=("sql", "schema", "nosql_schema", "nosql_query"),
        target_field="nosql_query",
        response_template="\n\nMongoDB:",
    ),
    TaskType.NOSQL2DOC.value: TaskSpec(
        task=TaskType.NOSQL2DOC,
        required_fields=("nosql_query", "nosql_schema", "documentation"),
        target_field="documentation",
        response_template="\n\nDocumentation:",
    ),
}


def get_task_spec(task: str | TaskType) -> TaskSpec:
    """Return the column map and response template for a training task."""
    if isinstance(task, TaskType):
        return TASK_SPECS[task.value]
    return TASK_SPECS[TaskType.from_str(task).value]


def format_task_prompt(task: str, prompt: str) -> str:
    """Prefix a generation prompt with the LoRA task identifier."""
    task_name = TaskType.from_str(task).value
    return f"Task: {task_name}\n\n{prompt.lstrip()}"


def get_target(row: dict[str, Any], task: str | TaskType) -> str:
    """Extract the supervised target string for a task."""
    spec = get_task_spec(task)
    return str(row.get(spec.target_field, "")).strip()


def get_training_dataset_configs(config: dict[str, Any] | None = None) -> tuple[str, ...]:
    """Return TEND subset names used for LoRA training (default: spider + bird train)."""
    if config is None:
        from src.utils.config import load_config

        config = load_config()
    training_cfg = config.get("training", {})
    datasets = training_cfg.get("datasets")
    if datasets:
        return tuple(str(name).strip().lower() for name in datasets)
    return DEFAULT_TRAINING_CONFIGS


def get_eval_dataset_configs(config: dict[str, Any] | None = None) -> tuple[str, ...]:
    """Return TEND subset names used for held-out eval during training."""
    if config is None:
        from src.utils.config import load_config

        config = load_config()
    training_cfg = config.get("training", {})
    datasets = training_cfg.get("eval_datasets")
    if datasets:
        return tuple(str(name).strip().lower() for name in datasets)
    return DEFAULT_EVAL_CONFIGS
