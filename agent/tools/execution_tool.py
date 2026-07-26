"""Tool 3 — execute SQL or Mongo shell queries."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Literal

from agent.config.settings import AgentSettings, get_settings
from agent.database.mongodb import MongoExecutor
from agent.database.postgres import PostgresExecutor
from agent.lib.sql_validation import validate_sql_for_execution

EngineKind = Literal["postgres", "mongo", "auto"]


def detect_engine(query: str) -> Literal["postgres", "mongo"]:
    text = (query or "").strip()
    if re.match(r"db\.\w+\.", text, re.IGNORECASE):
        return "mongo"
    return "postgres"


@dataclass(frozen=True)
class ExecutionResult:
    rows: list[dict[str, Any]]
    success: bool
    error: str | None
    row_count: int
    engine: str
    scalar: int | float | None = None
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExecutionTool:
    """Run read-only Postgres SELECT or Mongo shell queries."""

    def __init__(
        self,
        settings: AgentSettings | None = None,
        postgres: PostgresExecutor | None = None,
        mongo: MongoExecutor | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._postgres = postgres or PostgresExecutor(self._settings)
        self._mongo = mongo or MongoExecutor(self._settings)
        self._owns_postgres = postgres is None
        self._owns_mongo = mongo is None

    def close(self) -> None:
        if self._owns_postgres:
            self._postgres.close()
        if self._owns_mongo:
            self._mongo.close()

    def __enter__(self) -> ExecutionTool:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def run(
        self,
        query: str,
        *,
        engine: EngineKind = "auto",
        db_id: str | None = None,
        dataset: str | None = None,
        allowed_tables: set[str] | None = None,
    ) -> ExecutionResult:
        active_engine = detect_engine(query) if engine == "auto" else engine
        if active_engine == "mongo":
            return self._run_mongo(query, db_id=db_id, dataset=dataset)
        return self._run_postgres(
            query,
            db_id=db_id,
            dataset=dataset,
            allowed_tables=allowed_tables,
        )

    def _run_postgres(
        self,
        query: str,
        *,
        db_id: str | None,
        dataset: str | None,
        allowed_tables: set[str] | None,
    ) -> ExecutionResult:
        validation_error = validate_sql_for_execution(query, allowed_tables=allowed_tables)
        if validation_error:
            return ExecutionResult(
                rows=[],
                success=False,
                error=validation_error,
                row_count=0,
                engine="postgres",
            )

        result = self._postgres.execute(query, db_id=db_id, dataset=dataset)
        return ExecutionResult(
            rows=result.rows,
            success=result.ok,
            error=result.error,
            row_count=result.row_count,
            engine="postgres",
            truncated=result.truncated,
        )

    def _run_mongo(
        self,
        query: str,
        *,
        db_id: str | None,
        dataset: str | None,
    ) -> ExecutionResult:
        result = self._mongo.execute(query, db_id=db_id, dataset=dataset)
        rows = result.rows
        if result.scalar is not None:
            rows = [{"count": result.scalar}]
        return ExecutionResult(
            rows=rows,
            success=result.ok,
            error=result.error,
            row_count=result.row_count,
            engine="mongo",
            scalar=result.scalar,
            truncated=result.truncated,
        )


def execute_query(
    query: str,
    *,
    engine: EngineKind = "auto",
    db_id: str | None = None,
    dataset: str | None = None,
    allowed_tables: set[str] | None = None,
    settings: AgentSettings | None = None,
) -> dict[str, Any]:
    """Functional entry point for MCP / LangGraph."""
    with ExecutionTool(settings=settings) as tool:
        return tool.run(
            query,
            engine=engine,
            db_id=db_id,
            dataset=dataset,
            allowed_tables=allowed_tables,
        ).to_dict()
