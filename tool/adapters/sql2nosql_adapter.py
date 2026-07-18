"""SQL-to-NoSQL adapter — delegates to Sql2NoSqlPipeline."""

from __future__ import annotations

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger
from tool.pipeline.sql2nosql_pipeline import Sql2NoSqlPipeline, Sql2NoSqlPrepareResult


class Sql2NoSqlAdapter:
    name = "SQL-to-NoSQL"

    def __init__(self, pipeline: Sql2NoSqlPipeline | None = None):
        self.pipeline = pipeline or Sql2NoSqlPipeline()

    def prepare(self, user_input: str, *, logger: ActivityLogger) -> Sql2NoSqlPrepareResult | ExecuteResult:
        return self.pipeline.prepare(user_input, logger=logger)

    def execute_with_tables(
        self,
        user_input: str,
        prepare: Sql2NoSqlPrepareResult,
        selected_tables: list[str],
        *,
        logger: ActivityLogger,
    ) -> ExecuteResult:
        return self.pipeline.execute_with_tables(
            user_input,
            prepare,
            selected_tables,
            logger=logger,
        )

    def execute(self, user_input: str, *, logger: ActivityLogger) -> ExecuteResult:
        prepare = self.prepare(user_input, logger=logger)
        if isinstance(prepare, ExecuteResult):
            return prepare
        selected = [t.name for t in prepare.selection.selected]
        return self.execute_with_tables(user_input, prepare, selected, logger=logger)
