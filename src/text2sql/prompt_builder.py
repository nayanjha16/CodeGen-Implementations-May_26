"""Prompt builder for natural language to SQL generation."""

from __future__ import annotations

from typing import Any


class PromptBuilder:
    """Build prompts for text-to-SQL generation."""

    TEMPLATE = """Translate the question into SQL.

Rules:

* Use only schema tables and columns.
* Use JOIN when data spans multiple tables.
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
        return self.template.format(
            schema=schema.strip(),
            question=question.strip(),
        ).strip()

    def build_batch(self, examples: list[dict[str, str]]) -> list[str]:
        """Build prompts for a batch of examples."""
        return [
            self.build(ex["question"], ex.get("schema", ""))
            for ex in examples
        ]

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return "custom" if self.template != self.TEMPLATE else "default"
