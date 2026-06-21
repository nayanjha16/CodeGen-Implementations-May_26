"""SQL to MongoDB translation via the sql-mongo-converter PyPI package."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from sql_mongo_converter import sql_to_mongo

logger = logging.getLogger("codegen")

_SHELL_METHODS = {"find", "aggregate", "distinct"}
_AGG_SELECT_RE = re.compile(
    r"(count|avg|min|max|sum)\s*\(\s*(\*|\w+)\s*\)",
    re.IGNORECASE,
)


def _format_shell_doc(doc: dict[str, Any]) -> str:
    """Format a MongoDB document for shell output."""
    if not doc:
        return "{}"
    return json.dumps(doc, indent=2)


def mongo_dict_to_shell(mongo_obj: dict[str, Any]) -> str:
    """Render a sql-mongo-converter result dict as MongoDB shell syntax."""
    collection = mongo_obj.get("collection") or "collection"
    operation = mongo_obj.get("operation", "find")

    if operation == "aggregate":
        pipeline = mongo_obj.get("pipeline", [])
        return f"db.{collection}.aggregate(\n{_format_shell_doc(pipeline)}\n)"

    if operation == "distinct":
        field = mongo_obj.get("field", "_id")
        filter_doc = mongo_obj.get("find") or mongo_obj.get("filter") or {}
        return (
            f"db.{collection}.distinct(\n"
            f"  {json.dumps(field)},\n"
            f"  {_format_shell_doc(filter_doc)}\n"
            f")"
        )

    filter_doc = mongo_obj.get("find") or mongo_obj.get("filter") or {}
    projection = mongo_obj.get("projection")
    query = f"db.{collection}.find(\n  {_format_shell_doc(filter_doc)}"
    if projection:
        query += f",\n  {_format_shell_doc(projection)}"
    query += "\n)"

    sort_spec = mongo_obj.get("sort")
    if sort_spec:
        if isinstance(sort_spec, list):
            sort_doc = {field: direction for field, direction in sort_spec}
        else:
            sort_doc = sort_spec
        query += f".sort({_format_shell_doc(sort_doc)})"

    skip = mongo_obj.get("skip")
    if skip is not None:
        query += f".skip({skip})"

    limit = mongo_obj.get("limit")
    if limit is not None:
        query += f".limit({limit})"

    return query


def _promote_scalar_aggregates(mongo_obj: dict[str, Any], sql: str) -> dict[str, Any]:
    """Convert scalar aggregate find() output into an aggregate pipeline when needed."""
    if mongo_obj.get("operation") == "aggregate":
        return mongo_obj

    select_match = re.search(r"SELECT\s+(.*?)\s+FROM\b", sql, re.IGNORECASE | re.DOTALL)
    if not select_match:
        return mongo_obj

    aggregates = list(_AGG_SELECT_RE.finditer(select_match.group(1)))
    if not aggregates:
        return mongo_obj

    filter_doc = mongo_obj.get("find") or mongo_obj.get("filter") or {}
    group_stage: dict[str, Any] = {"_id": None}
    for index, match in enumerate(aggregates, start=1):
        func = match.group(1).lower()
        column = match.group(2)
        alias = func if len(aggregates) == 1 else f"{func}_{index}"
        if func == "count" and column == "*":
            group_stage[alias] = {"$sum": 1}
            continue
        mongo_func = {
            "count": "$sum",
            "avg": "$avg",
            "min": "$min",
            "max": "$max",
            "sum": "$sum",
        }[func]
        group_stage[alias] = {mongo_func: f"${column}"}

    pipeline: list[dict[str, Any]] = []
    if filter_doc:
        pipeline.append({"$match": filter_doc})
    pipeline.append({"$group": group_stage})

    promoted = {
        "collection": mongo_obj.get("collection", ""),
        "operation": "aggregate",
        "pipeline": pipeline,
    }
    if filter_doc:
        promoted["find"] = filter_doc
    return promoted


class SQLToNoSQLTranslator:
    """Translate SQL SELECT queries to MongoDB shell syntax using sql-mongo-converter."""

    UNSUPPORTED_WARNINGS: list[str] = []

    def translate(self, sql: str) -> dict[str, Any]:
        """Translate SQL to MongoDB query string and structured parts."""
        self.UNSUPPORTED_WARNINGS = []
        sql = sql.strip().rstrip(";")
        if not sql:
            return self._failure("Empty SQL query")

        if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
            return self._failure("Only SELECT queries are supported for translation")

        upper_sql = sql.upper()
        if "UNION" in upper_sql:
            self._warn("UNION is not supported")

        try:
            mongo_obj = sql_to_mongo(sql, allow_mutations=False)
        except ValueError as exc:
            return self._failure(str(exc))
        except Exception as exc:
            logger.exception("sql-mongo-converter failed for SQL: %s", sql)
            return self._failure(f"Translation failed: {exc}")

        if not mongo_obj:
            return self._failure("sql-mongo-converter returned an empty result")

        mongo_obj = _promote_scalar_aggregates(mongo_obj, sql)

        operation = mongo_obj.get("operation", "find")
        if operation not in _SHELL_METHODS:
            return self._failure(
                f"Unsupported MongoDB operation for SELECT translation: {operation}"
            )

        mongodb_query = mongo_dict_to_shell(mongo_obj)
        filter_doc = mongo_obj.get("find") or mongo_obj.get("filter") or {}
        projection = mongo_obj.get("projection") or {}
        if projection is None:
            projection = {}

        result: dict[str, Any] = {
            "mongodb_query": mongodb_query,
            "collection": mongo_obj.get("collection", ""),
            "filter": filter_doc,
            "projection": projection,
            "warnings": list(self.UNSUPPORTED_WARNINGS),
            "success": True,
        }
        if operation == "aggregate":
            result["pipeline"] = mongo_obj.get("pipeline", [])
        return result

    def _failure(self, message: str) -> dict[str, Any]:
        return {
            "mongodb_query": "",
            "collection": "",
            "filter": {},
            "projection": {},
            "warnings": [message],
            "success": False,
        }

    def _warn(self, message: str) -> None:
        logger.warning(message)
        self.UNSUPPORTED_WARNINGS.append(message)
