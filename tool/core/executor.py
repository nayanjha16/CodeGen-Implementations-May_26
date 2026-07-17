"""Read-only SQL execution returning a pandas DataFrame."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from tool.core.activity_logger import ActivityLogger


@dataclass
class ExecutionResult:
    dataframe: pd.DataFrame
    row_count: int
    duration_ms: float
    truncated: bool
    sql: str


def execute_readonly_sql(
    engine: Engine,
    sql: str,
    *,
    max_rows: int = 1000,
    timeout_sec: int = 30,
    logger: ActivityLogger | None = None,
) -> ExecutionResult:
    """Execute read-only SQL and return capped results."""
    if logger:
        logger.info(stage="execution", event="executing", message="Running validated SQL query")

    start = time.perf_counter()
    limited_sql = f"SELECT * FROM ({sql.rstrip(';')}) AS _sub LIMIT {max_rows + 1}"

    with engine.connect() as conn:
        conn = conn.execution_options(postgresql_readonly=True)
        result = conn.execute(text(limited_sql))
        rows = result.fetchall()
        columns = list(result.keys())

    duration_ms = (time.perf_counter() - start) * 1000
    truncated = len(rows) > max_rows
    if truncated:
        rows = rows[:max_rows]

    df = pd.DataFrame(rows, columns=columns)
    if logger:
        logger.info(
            stage="execution",
            event="rows_retrieved",
            message="Query execution complete",
            details={
                "row_count": len(df),
                "duration_ms": round(duration_ms, 1),
                "truncated": truncated,
            },
        )

    return ExecutionResult(
        dataframe=df,
        row_count=len(df),
        duration_ms=duration_ms,
        truncated=truncated,
        sql=sql,
    )
