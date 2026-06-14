"""Validation helpers for TEND dataset generation."""

from __future__ import annotations

import json
import re
from typing import Any


def validate_sql_schema(sql_schema: str) -> dict[str, Any]:
    """Check that SQL schema contains CREATE TABLE statements."""
    tables = re.findall(r"CREATE\s+TABLE\s+\w+", sql_schema, flags=re.IGNORECASE)
    return {"valid": bool(tables), "table_count": len(tables)}


def validate_sql_query(sql_query: str) -> dict[str, Any]:
    """Check that SQL query looks like a SELECT statement."""
    valid = bool(re.match(r"^\s*SELECT\b", sql_query or "", re.IGNORECASE))
    return {"valid": valid}


def validate_mongo_schema(nosql_schema: str | dict[str, Any]) -> dict[str, Any]:
    """Check that Mongo schema is non-empty JSON object."""
    if isinstance(nosql_schema, str):
        try:
            parsed = json.loads(nosql_schema)
        except json.JSONDecodeError:
            return {"valid": False, "collection_count": 0}
    else:
        parsed = nosql_schema
    valid = isinstance(parsed, dict) and bool(parsed)
    return {"valid": valid, "collection_count": len(parsed) if isinstance(parsed, dict) else 0}


def validate_mongo_query(nosql_query: str) -> dict[str, Any]:
    """Check whether Mongo query uses supported shell methods."""
    q = (nosql_query or "").strip()
    valid = bool(re.match(r"db\.\w+\.(find|aggregate|distinct)\s*\(", q))
    return {"valid": valid}


def validate_conversion(nosql_query: str, conversion_success: bool) -> dict[str, Any]:
    """Validate end-to-end conversion success."""
    query_check = validate_mongo_query(nosql_query)
    return {
        "conversion_success": conversion_success and query_check["valid"],
        "query_valid": query_check["valid"],
    }
