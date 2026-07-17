"""Prompt builder for natural language to SQL generation."""

from __future__ import annotations

from typing import Any

from src.training.tasks import TaskType, format_task_prompt


class PromptBuilder:
    """Build prompts for text-to-SQL generation."""

    TEMPLATE = """Translate the question into SQL.

Rules:

* Use only schema tables and columns.
* Use a single table when the question only needs data from one table; avoid unnecessary JOINs.
* JOIN when selected columns, filters, or aggregations require data from more than one table.
* Follow FOREIGN KEY relationships in the schema for JOIN keys: child_table.fk_column = parent_table.referred_column.
* For many-to-many links, JOIN through the association table that references both sides.
* Apply each filter to the table and column that owns that attribute in the schema.
* Prefer explicit INNER JOIN ... ON ...; use LEFT JOIN only when the question needs rows with missing optional related data.
* Qualify column names with table names or aliases when the same name appears in multiple tables.
* Use COUNT(*) for counts.
* Use DISTINCT when uniqueness is required.
* Use GROUP BY for aggregations by category.
* Use ORDER BY for ranking or sorting.
* Use LIMIT when the question asks for top, highest, lowest, first, or last.
* Return exactly one SQL SELECT statement.

Schema:
{schema}

Question:
{question}

SQL:
"""

    def __init__(self, template: str | None = None):
        self.template = template or self.TEMPLATE

    @classmethod
    def for_model(cls, model_name: str, config: dict[str, Any] | None = None) -> "PromptBuilder":
        """Create a prompt builder for the given model."""
        return cls()

    def build(self, question: str, schema: str) -> str:
        """Build a text-to-SQL prompt."""
        prompt = self.template.format(
            schema=schema.strip(),
            question=question.strip(),
        ).strip()
        return format_task_prompt(TaskType.TEXT2SQL.value, prompt)

    def build_batch(self, examples: list[dict[str, str]]) -> list[str]:
        """Build prompts for a batch of examples."""
        return [
            self.build(ex["question"], ex.get("schema", ""))
            for ex in examples
        ]

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return "custom" if self.template != self.TEMPLATE else "default"
