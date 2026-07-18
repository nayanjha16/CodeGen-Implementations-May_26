"""Adapter registry for desktop tab extensibility."""

from __future__ import annotations

from tool.adapters.base import QueryAdapter
from tool.adapters.sql2nosql_adapter import Sql2NoSqlAdapter
from tool.adapters.text2sql_adapter import Text2SqlAdapter
from tool.pipeline.sql2nosql_pipeline import Sql2NoSqlPipeline
from tool.pipeline.text2sql_pipeline import Text2SqlPipeline


def build_adapters(
    *,
    pipeline: Text2SqlPipeline | None = None,
    sql2nosql_pipeline: Sql2NoSqlPipeline | None = None,
) -> dict[str, QueryAdapter]:
    """Return tab-name → adapter mapping. Add new adapters here."""
    text2sql = Text2SqlAdapter(pipeline or Text2SqlPipeline())
    sql2nosql = Sql2NoSqlAdapter(sql2nosql_pipeline or Sql2NoSqlPipeline())
    return {
        "Text-to-SQL": text2sql,
        "SQL-to-NoSQL": sql2nosql,
    }
