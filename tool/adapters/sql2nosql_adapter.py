"""SQL-to-NoSQL adapter — delegates to Sql2NoSqlPipeline."""

from __future__ import annotations

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger
from tool.pipeline.sql2nosql_pipeline import Sql2NoSqlPipeline


class Sql2NoSqlAdapter:
    name = "SQL-to-NoSQL"

    def __init__(self, pipeline: Sql2NoSqlPipeline | None = None):
        self.pipeline = pipeline or Sql2NoSqlPipeline()

    def execute(self, user_input: str, *, logger: ActivityLogger) -> ExecuteResult:
        return self.pipeline.execute(user_input, logger=logger)
