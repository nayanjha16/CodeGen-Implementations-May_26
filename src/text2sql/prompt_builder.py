"""Prompt builder for natural language to SQL generation."""

from __future__ import annotations

from typing import Any


class PromptBuilder:
    """Build prompts for CodeGen text-to-SQL generation."""

    DEFAULT_TEMPLATE = """Schema:
{schema}

Question:
{question}

Generate SQL query.
"""

    def __init__(self, template: str | None = None):
        self.template = template or self.DEFAULT_TEMPLATE

    def build(self, question: str, schema: str) -> str:
        """Build a prompt from question and schema."""
        return self.template.format(
            schema=schema.strip(),
            question=question.strip(),
        ).strip()

    def build_batch(
        self, examples: list[dict[str, str]]
    ) -> list[str]:
        """Build prompts for a batch of examples."""
        return [
            self.build(ex["question"], ex.get("schema", ""))
            for ex in examples
        ]

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        if self.template == self.DEFAULT_TEMPLATE:
            return "default"
        return "custom"
