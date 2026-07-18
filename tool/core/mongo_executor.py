"""Execute MongoDB shell queries against configured databases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
from pymongo.collection import Collection
from pymongo.database import Database

from tool.core.activity_logger import ActivityLogger
from tool.core.mongo_shell_parser import ParsedShellQuery, ShellParseError, parse_shell_query


@dataclass(frozen=True)
class MongoExecutionResult:
    dataframe: pd.DataFrame
    row_count: int
    duration_ms: float
    scalar: int | float | None = None
    truncated: bool = False
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _normalize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, memoryview):
        return bytes(value)
    return value


def _normalize_document(doc: dict[str, Any]) -> dict[str, Any]:
    return {str(key).lower(): _normalize_value(value) for key, value in doc.items()}


def _execute_parsed_query(
    db: Database,
    parsed: ParsedShellQuery,
    *,
    max_rows: int,
    max_time_ms: int,
) -> MongoExecutionResult:
    collection: Collection = db[parsed.collection.lower()]
    method = parsed.method

    if method == "find":
        filter_doc = parsed.args[0] if parsed.args else {}
        projection = parsed.args[1] if len(parsed.args) > 1 else None
        if not isinstance(filter_doc, dict):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="find() filter must be an object")
        if projection is not None and not isinstance(projection, dict):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="find() projection must be an object")

        cursor = collection.find(filter_doc, projection or None, max_time_ms=max_time_ms)
        if parsed.sort:
            cursor = cursor.sort(list(parsed.sort.items()))
        if parsed.skip is not None:
            cursor = cursor.skip(parsed.skip)
        limit = parsed.limit if parsed.limit is not None else max_rows + 1
        cursor = cursor.limit(limit)
        rows = [_normalize_document(doc) for doc in cursor]
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        df = pd.DataFrame(rows)
        return MongoExecutionResult(df, len(rows), 0.0, truncated=truncated)

    if method == "aggregate":
        if not parsed.args:
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="aggregate() requires a pipeline")
        pipeline = parsed.args[0]
        if not isinstance(pipeline, list):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="aggregate() pipeline must be an array")
        if parsed.sort or parsed.skip is not None or parsed.limit is not None:
            return MongoExecutionResult(
                pd.DataFrame(),
                0,
                0.0,
                error="Chained sort/skip/limit is not supported on aggregate()",
            )
        rows = [
            _normalize_document(doc)
            for doc in collection.aggregate(pipeline, maxTimeMS=max_time_ms)
        ]
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        return MongoExecutionResult(pd.DataFrame(rows), len(rows), 0.0, truncated=truncated)

    if method == "countdocuments":
        filter_doc = parsed.args[0] if parsed.args else {}
        if not isinstance(filter_doc, dict):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="countDocuments() filter must be an object")
        count = int(collection.count_documents(filter_doc, maxTimeMS=max_time_ms))
        df = pd.DataFrame([{"count": count}])
        return MongoExecutionResult(df, 1, 0.0, scalar=count)

    if method == "distinct":
        if not parsed.args:
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="distinct() requires a field name")
        field = parsed.args[0]
        filter_doc = parsed.args[1] if len(parsed.args) > 1 else {}
        if not isinstance(field, str):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="distinct() field must be a string")
        if not isinstance(filter_doc, dict):
            return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error="distinct() filter must be an object")
        values = collection.distinct(field, filter_doc, maxTimeMS=max_time_ms)
        rows = [{field.lower(): _normalize_value(value)} for value in values]
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        return MongoExecutionResult(pd.DataFrame(rows), len(rows), 0.0, truncated=truncated)

    return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error=f"Unsupported method: {method}")


def execute_mongo_query(
    db: Database,
    nosql_query: str,
    *,
    max_rows: int = 1000,
    max_time_ms: int = 30_000,
    logger: ActivityLogger | None = None,
) -> MongoExecutionResult:
    """Run a MongoDB shell query string against *db*."""
    import time

    start = time.perf_counter()
    try:
        parsed = parse_shell_query(nosql_query)
    except ShellParseError as exc:
        return MongoExecutionResult(pd.DataFrame(), 0, 0.0, error=str(exc))

    if logger:
        logger.info(
            stage="execution",
            event="executing",
            message="Executing MongoDB query",
            details={"collection": parsed.collection, "method": parsed.method},
        )

    try:
        result = _execute_parsed_query(db, parsed, max_rows=max_rows, max_time_ms=max_time_ms)
        duration_ms = (time.perf_counter() - start) * 1000
        if result.error:
            return MongoExecutionResult(result.dataframe, result.row_count, duration_ms, error=result.error)
        return MongoExecutionResult(
            result.dataframe,
            result.row_count,
            duration_ms,
            scalar=result.scalar,
            truncated=result.truncated,
        )
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return MongoExecutionResult(pd.DataFrame(), 0, duration_ms, error=str(exc))


def validate_mongo_query(nosql_query: str) -> dict[str, Any]:
    """Validate MongoDB shell syntax without executing."""
    try:
        parsed = parse_shell_query(nosql_query)
        return {
            "passed": True,
            "message": f"Valid {parsed.method}() on {parsed.collection}",
            "collection": parsed.collection,
            "method": parsed.method,
        }
    except ShellParseError as exc:
        return {"passed": False, "message": str(exc), "reason": "parse_error"}
