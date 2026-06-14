"""SQL query to MongoDB query conversion for TEND pipeline."""

from __future__ import annotations

from typing import Any

from src.sql2nosql.translator import SQLToNoSQLTranslator


def convert_query(
    sql_query: str,
    translator: SQLToNoSQLTranslator | None = None,
) -> dict[str, Any]:
    """Convert a SQL query into MongoDB shell syntax and structured parts."""
    tr = translator or SQLToNoSQLTranslator()
    result = tr.translate(sql_query)
    return {
        "nosql_query": result.get("mongodb_query", ""),
        "collection": result.get("collection", ""),
        "filter": result.get("filter", {}),
        "projection": result.get("projection", {}),
        "warnings": result.get("warnings", []),
        "success": bool(result.get("success")),
    }
