"""Prompt builder for natural language to SQL generation."""

from __future__ import annotations

import re
from typing import Any


class PromptBuilder:
    """Build prompts for text-to-SQL generation."""

    DEFAULT_TEMPLATE = """The database tables already exist. Do not create or modify tables.
Write only a single SQL SELECT query to answer the question.
Do not execute the query or show its results. Output the SQL query only—no "Output" section, MongoDB schema, Python code, explanations, or any other text after the query.

SQL Schema:
{sql_schema}

Question:
{question}

SQL:"""

    CAUSAL_LM_TEMPLATE = """Task: write one SQL SELECT query only.

Rules:
- Use only the tables and columns listed in the SQL schema below.
- Return exactly one complete SQL SELECT statement, then stop.
- Do not write Python, MongoDB, JavaScript, C++, or any other programming language.
- Do not write MongoDB schema JSON, imports (e.g. import sqlite3), #include, connection code, or scripts.
- Do not execute the query or print results (no "Output:" section or sample rows).
- Do not repeat "SQL:" or generate multiple queries.

SQL Schema:
{sql_schema}

Question:
{question}

SQL:"""

    SEQ2SEQ_TEMPLATE = """The database tables already exist. Do not create or modify tables.
Write only a single SQL SELECT query.
Do not execute the query or show its results. Output the SQL query only—no MongoDB, Python, or other text after the query.

Question: {question}
SQL Schema: {sql_schema}
SQL:"""

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
    def for_model(cls, model_name: str, config: dict[str, Any] | None = None) -> "PromptBuilder":
        """Pick a prompt template suited to the model family."""
        config = config or {}
        text2sql_cfg = config.get("text2sql", {})
        requested = text2sql_cfg.get("prompt_template", "auto")

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

    def build(
        self,
        question: str,
        schema: str,
    ) -> str:
        """Build a SQL-only text-to-SQL prompt (no MongoDB schema)."""
        sql_schema = schema.strip()

        formatted_sql_schema = sql_schema
        if self.template_name == "seq2seq":
            formatted_sql_schema = self.compact_schema(sql_schema)

        return self.template.format(
            sql_schema=formatted_sql_schema,
            question=question.strip(),
        ).strip()

    def build_batch(
        self, examples: list[dict[str, str]]
    ) -> list[str]:
        """Build prompts for a batch of examples."""
        return [
            self.build(
                ex["question"],
                ex.get("schema", ""),
            )
            for ex in examples
        ]

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return self.template_name
