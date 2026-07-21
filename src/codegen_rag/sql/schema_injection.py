"""Renders a `DatabaseSchema` into the compact textual prompt prefix used for
schema injection ahead of natural-language-to-SQL generation.
"""

from __future__ import annotations

from codegen_rag.sql.schema import DatabaseSchema


def build_schema_prompt(schema: DatabaseSchema, include_sample_values: bool = True, max_sample_chars: int = 60) -> str:
    """Render CREATE-TABLE-style text plus a few sample rows per table.

    Example output::

        # Database: concert_singer
        # Table: singer(Singer_ID, Name, Country, Age)
        #   sample row: (1, 'Joe Sharp', 'Netherlands', 52)
        # Table: concert(concert_ID, concert_Name, Theme, Year)
    """
    lines = [f"# Database: {schema.db_id}"]
    for table in schema.tables:
        column_list = ", ".join(c.name for c in table.columns)
        lines.append(f"# Table: {table.name}({column_list})")
        if include_sample_values and table.sample_rows:
            row = table.sample_rows[0]
            row_str = ", ".join(_truncate(str(v), max_sample_chars) for v in row)
            lines.append(f"#   sample row: ({row_str})")
    return "\n".join(lines)


def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


def build_sql_prompt(
    question: str,
    schema: DatabaseSchema,
    include_sample_values: bool = True,
    few_shot_examples: list[tuple[str, str]] | None = None,
) -> str:
    """Full text-to-SQL prompt: schema prefix + optional few-shot examples
    (used by the RAG pipeline in Checkpoint 3 to inject retrieved
    question/SQL pairs) + the target question.
    """
    parts = [build_schema_prompt(schema, include_sample_values)]

    if few_shot_examples:
        parts.append("# Similar examples:")
        for example_question, example_sql in few_shot_examples:
            parts.append(f"# Q: {example_question}\n# SQL: {example_sql}")

    parts.append(f"# Question: {question}\n# SQL:")
    return "\n".join(parts)
