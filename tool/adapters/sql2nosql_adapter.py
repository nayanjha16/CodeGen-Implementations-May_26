"""SQL-to-NoSQL adapter stub."""

from __future__ import annotations

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger


class Sql2NoSqlAdapter:
    name = "SQL-to-NoSQL"

    def execute(self, user_input: str, *, logger: ActivityLogger) -> ExecuteResult:
        logger.warning(
            stage="adapter",
            event="not_implemented",
            message="SQL-to-NoSQL is not yet implemented",
        )
        return ExecuteResult(success=False, error="SQL-to-NoSQL coming soon")
