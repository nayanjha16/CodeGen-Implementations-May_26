"""Build prompts for SQL-to-MongoDB conversion."""

from __future__ import annotations

import re
from typing import Any


class NoSQLPromptBuilder:
    """Build prompts for converting SQL queries to MongoDB shell syntax."""

    DEFAULT_TEMPLATE = """The MongoDB collections already exist. Do not create or modify collections.
Convert the SQL query below into a single MongoDB shell query.
Use db.<collection>.find(), db.<collection>.aggregate(), or db.<collection>.distinct().
Output the MongoDB query only—no explanations, SQL, Python code, or other text after the query.

SQL Schema:
{sql_schema}

SQL Query:
{sql_query}

MongoDB Schema:
{nosql_schema}

MongoDB Query:"""

    CAUSAL_LM_TEMPLATE = """Task: convert one SQL query to a MongoDB shell query only.

Rules:
- Use only the collections and fields listed in the MongoDB schema below.
- Translate the SQL query into exactly one MongoDB query using db.<collection>.find(), aggregate(), or distinct().
- Output must start with db.<collection>. and contain only MongoDB shell syntax.
- Do not write SQL, Python, JavaScript, JSON schema dumps, code examples, or explanations.
- Do not write sections such as "Python Query:", "JavaScript Query:", or "Python Example:".
- Do not execute the query or print results.
- Do not repeat "MongoDB:" or generate multiple queries.

SQL Schema:
{sql_schema}

SQL Query:
{sql_query}

MongoDB Schema:
{nosql_schema}

MongoDB Query:"""

    SEQ2SEQ_TEMPLATE = """The MongoDB collections already exist. Do not create or modify collections.
Convert the SQL query below into a single MongoDB shell query.
Output the MongoDB query only—no extra text after the query.

SQL Schema: {sql_schema}
SQL Query: {sql_query}
MongoDB Schema: {nosql_schema}
MongoDB Query:"""

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

    def build(
        self,
        sql_query: str,
        schema: str,
        nosql_schema: str | None = None,
    ) -> str:
        """Build a prompt from SQL query, SQL schema, and MongoDB schema."""
        from src.utils.schema_conversion import derive_mongo_schema_json

        sql_schema = schema.strip()
        mongo_schema = nosql_schema
        if mongo_schema is None:
            mongo_schema = derive_mongo_schema_json(
                sql_schema, compact=self.template_name == "seq2seq"
            )
        else:
            mongo_schema = mongo_schema.strip() or "{}"

        formatted_sql_schema = sql_schema
        if self.template_name == "seq2seq":
            formatted_sql_schema = self.compact_schema(sql_schema)

        return self.template.format(
            sql_schema=formatted_sql_schema,
            nosql_schema=mongo_schema,
            sql_query=sql_query.strip(),
        ).strip()

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return self.template_name
