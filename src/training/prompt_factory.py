"""Map training tasks to runtime prompt builders."""

from __future__ import annotations

from typing import Any

from src.training.tasks import TaskType, get_task_spec
from src.utils.config import get_model_name


def build_training_prompt(
    row: dict[str, str],
    task: str,
    *,
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
) -> str:
    """Build the inference-aligned prompt for one TEND row and task."""
    from src.documentation.prompt_builder import DocumentationPromptBuilder
    from src.sql2nosql.prompt_builder import NoSQLPromptBuilder
    from src.text2sql.prompt_builder import PromptBuilder

    cfg = config or {}
    name = model_name or get_model_name(cfg)
    task_type = TaskType.from_str(task)

    if task_type is TaskType.TEXT2SQL:
        return PromptBuilder.for_model(name, cfg).build(
            row["question"],
            row.get("schema", ""),
        )

    if task_type is TaskType.SQL2NOSQL:
        return NoSQLPromptBuilder.for_model(name, cfg).build(
            row["sql"],
            row.get("schema", ""),
            nosql_schema=row.get("nosql_schema"),
        )

    if task_type is TaskType.NOSQL2DOC:
        return DocumentationPromptBuilder.for_model(name, cfg).build(
            row["nosql_query"],
            row.get("schema", ""),
            nosql_schema=row.get("nosql_schema"),
            question=row.get("question", ""),
        )

    raise ValueError(f"Unsupported task: {task}")


def build_training_target(row: dict[str, str], task: str) -> str:
    """Return the supervised completion target for one row."""
    spec = get_task_spec(task)
    return str(row.get(spec.target_field, "")).strip()
