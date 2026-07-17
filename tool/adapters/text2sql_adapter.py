"""Text-to-SQL adapter — delegates to Text2SqlPipeline."""

from __future__ import annotations

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger
from tool.pipeline.text2sql_pipeline import PrepareResult, Text2SqlPipeline


class Text2SqlAdapter:
    name = "Text-to-SQL"

    def __init__(self, pipeline: Text2SqlPipeline | None = None):
        self.pipeline = pipeline or Text2SqlPipeline()

    def prepare(self, user_input: str, *, logger: ActivityLogger) -> PrepareResult | ExecuteResult:
        return self.pipeline.prepare(user_input, logger=logger)

    def execute_with_tables(
        self,
        user_input: str,
        prepare: PrepareResult,
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
        return self.pipeline.run(user_input, logger=logger)
