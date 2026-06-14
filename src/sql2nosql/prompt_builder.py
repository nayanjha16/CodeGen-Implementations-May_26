"""Build prompts for text-to-MongoDB generation."""

from __future__ import annotations

import re
from typing import Any


class NoSQLPromptBuilder:
    """Build prompts for MongoDB shell query generation."""

    DEFAULT_TEMPLATE = """The MongoDB collections already exist. Do not create or modify collections.
Write only a single MongoDB shell query to answer the question.
Use db.<collection>.find(), db.<collection>.aggregate(), or db.<collection>.distinct().
Output the MongoDB query only—no explanations, SQL, Python code, or other text after the query.

Schema:
{schema}

Question:
{question}

MongoDB:"""

    CAUSAL_LM_TEMPLATE = """Task: write one MongoDB shell query only.

Rules:
- Use only the collections and fields listed in the schema below.
- Return exactly one MongoDB query using db.<collection>.find(), aggregate(), or distinct().
- Do not write SQL, Python, JavaScript functions, or explanations.
- Do not execute the query or print results.
- Do not repeat "MongoDB:" or generate multiple queries.

Schema:
{schema}

Question:
{question}

MongoDB:"""

    SEQ2SEQ_TEMPLATE = """The MongoDB collections already exist. Do not create or modify collections.
Write only a single MongoDB shell query.
Output the MongoDB query only—no extra text after the query.

Question: {question}
Schema: {schema}
MongoDB:"""

    TEMPLATES = {
        "default": DEFAULT_TEMPLATE,
        "causal": CAUSAL_LM_TEMPLATE,
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
    def for_model(cls, model_name: str, config: dict[str, Any] | None = None) -> "NoSQLPromptBuilder":
        """Pick a prompt template based on model type and config."""
        config = config or {}
        sql2nosql_cfg = config.get("sql2nosql", {})
        requested = sql2nosql_cfg.get("prompt_template", "auto")

        if requested == "auto":
            from src.models.model_loader import is_seq2seq_model

            has_checkpoint = bool((config or {}).get("model", {}).get("checkpoint"))
            if is_seq2seq_model(model_name) and has_checkpoint:
                template_name = "seq2seq"
            elif is_seq2seq_model(model_name):
                template_name = "default"
            else:
                template_name = "causal"
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

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return self.template_name
