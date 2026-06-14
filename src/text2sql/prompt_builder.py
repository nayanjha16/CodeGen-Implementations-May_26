"""Prompt builder for natural language to SQL generation."""

from __future__ import annotations

import re
from typing import Any


class PromptBuilder:
    """Build prompts for text-to-SQL generation."""

    DEFAULT_TEMPLATE = """Schema:
{schema}

Question:
{question}

Generate SQL query.
"""

    SEQ2SEQ_TEMPLATE = """Question: {question}
Schema: {schema}
SQL:"""

    TEMPLATES = {
        "default": DEFAULT_TEMPLATE,
        "seq2seq": SEQ2SEQ_TEMPLATE,
    }

    def __init__(self, template: str | None = None, template_name: str = "default"):
        if template is not None:
            self.template = template
            self.template_name = "custom"
        else:
            self.template_name = template_name
            self.template = self.TEMPLATES.get(template_name, self.DEFAULT_TEMPLATE)

    @classmethod
    def for_model(cls, model_name: str, config: dict[str, Any] | None = None) -> "PromptBuilder":
        """Pick a prompt template suited to the model family."""
        config = config or {}
        text2sql_cfg = config.get("text2sql", {})
        requested = text2sql_cfg.get("prompt_template", "auto")

        if requested == "auto":
            from src.models.model_loader import is_seq2seq_model

            has_checkpoint = bool((config or {}).get("model", {}).get("checkpoint"))
            # Fine-tuned seq2seq checkpoints expect the compact seq2seq prompt;
            # base models (including unfine-tuned T5) use the default template.
            if is_seq2seq_model(model_name) and has_checkpoint:
                template_name = "seq2seq"
            else:
                template_name = "default"
        elif requested in cls.TEMPLATES:
            template_name = requested
        else:
            template_name = "default"

        return cls(template_name=template_name)

    @staticmethod
    def compact_schema(schema: str) -> str:
        """Convert multi-line schema text to a compact single-line form."""
        parts = []
        for line in schema.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"^Table\s+", "", line, flags=re.IGNORECASE)
            parts.append(line)
        return " | ".join(parts)

    def build(self, question: str, schema: str) -> str:
        """Build a prompt from question and schema."""
        formatted_schema = schema.strip()
        if self.template_name == "seq2seq":
            formatted_schema = self.compact_schema(schema)

        return self.template.format(
            schema=formatted_schema,
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
        return self.template_name
