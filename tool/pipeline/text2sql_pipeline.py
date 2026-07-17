"""End-to-end Text-to-SQL Execute pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy.engine import Engine

from src.text2sql.prompt_builder import PromptBuilder

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger
from tool.core.database import get_active_engine
from tool.core.executor import execute_readonly_sql
from tool.core.inference.fastapi_client import FastApiInferenceClient
from tool.core.safety_validator import SafetyValidator
from tool.core.schema_loader import TableSchema, load_all_tables
from tool.core.schema_selector import SchemaSelectionResult, build_schema_ddl, select_tables_for_prompt
from tool.core.settings_store import AppSettings, DatabaseConnection, SettingsStore


@dataclass
class PrepareResult:
    """Connection + schema state after auto table selection, before user confirmation."""

    engine: Engine
    conn: DatabaseConnection
    all_tables: list[TableSchema]
    selection: SchemaSelectionResult
    question: str


class Text2SqlPipeline:
    """Orchestrate connect → schema → inference → validate → execute."""

    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or SettingsStore().load()
        self.prompt_builder = PromptBuilder()
        self.validator = SafetyValidator()

    def run(self, question: str, *, logger: ActivityLogger) -> ExecuteResult:
        """Full pipeline using auto-selected tables (no user confirmation step)."""
        prepare = self.prepare(question, logger=logger)
        if isinstance(prepare, ExecuteResult):
            return prepare
        selected = [t.name for t in prepare.selection.selected]
        return self.execute_with_tables(question, prepare, selected, logger=logger)

    def prepare(self, question: str, *, logger: ActivityLogger) -> PrepareResult | ExecuteResult:
        """Connect, load schema, and suggest relevant tables for user review."""
        question = question.strip()
        if not question:
            return ExecuteResult(success=False, error="Please enter a natural language question.")

        logger.info(
            stage="inference",
            event="inference_mode_selected",
            message="Using FastAPI inference endpoint",
            details={"mode": "fastapi", "model": self.settings.fastapi.model},
        )

        try:
            engine, conn = get_active_engine(self.settings)
            logger.info(
                stage="connection",
                event="connection_established",
                message="Connected to PostgreSQL",
                details={"connection": conn.name, "database": conn.database, "schema": conn.schema},
            )
        except Exception as exc:
            logger.error(
                stage="connection",
                event="connection_failed",
                message="Failed to connect to database",
                details={"error": str(exc)},
            )
            return ExecuteResult(success=False, error=str(exc))

        logger.info(stage="render", event="render_start", message="Starting schema selection")

        try:
            logger.info(stage="schema", event="schema_load_start", message="Loading database schema")
            all_tables = load_all_tables(engine, schema=conn.schema)
            logger.info(
                stage="schema",
                event="schema_loaded",
                message="Schema introspection complete",
                details={"table_count": len(all_tables), "schema": conn.schema},
            )

            selection = select_tables_for_prompt(
                question,
                all_tables,
                embedding_model=self.settings.schema_selection.embedding_model,
                top_k=self.settings.schema_selection.top_k,
                min_score=self.settings.schema_selection.min_score,
                logger=logger,
            )
            return PrepareResult(
                engine=engine,
                conn=conn,
                all_tables=all_tables,
                selection=selection,
                question=question,
            )
        except Exception as exc:
            logger.error(
                stage="pipeline",
                event="pipeline_failed",
                message="Schema preparation failed",
                details={"error": str(exc)},
            )
            return ExecuteResult(success=False, error=str(exc))

    def execute_with_tables(
        self,
        question: str,
        prepare: PrepareResult,
        selected_names: list[str],
        *,
        logger: ActivityLogger,
    ) -> ExecuteResult:
        """Generate SQL (visible before execution), validate, and run the query."""
        question = question.strip()
        if not selected_names:
            return ExecuteResult(success=False, error="Select at least one table before running the query.")

        table_by_name = {t.name: t for t in prepare.all_tables}
        missing = [name for name in selected_names if name not in table_by_name]
        if missing:
            return ExecuteResult(
                success=False,
                error=f"Unknown tables: {', '.join(missing)}",
            )

        selected_tables = [table_by_name[name] for name in selected_names]
        schema_ddl = build_schema_ddl(selected_tables)
        render_start = time.perf_counter()
        sql: str | None = None

        try:
            prompt = self.prompt_builder.build(question, schema_ddl)
            logger.info(
                stage="prompt",
                event="prompt_built",
                message="Built text-to-SQL prompt with selected schema",
                details={"prompt_length": len(prompt), "tables": selected_names},
            )
            logger.info(
                stage="prompt",
                event="prompt_body",
                message="Full prompt payload",
                details={"prompt": prompt},
            )

            client = FastApiInferenceClient(self.settings.fastapi, logger=logger)
            sql = client.generate_sql(prompt)
            if not sql:
                logger.error(
                    stage="inference",
                    event="sql_generation_failed",
                    message="Could not extract SQL from API response",
                )
                return ExecuteResult(
                    success=False,
                    generated_sql=None,
                    selected_tables=selected_names,
                    error="Could not extract SQL from model response.",
                )

            logger.info(stage="validation", event="validation_start", message="Validating generated SQL")
            validation = self.validator.validate(sql)
            if not validation["passed"]:
                logger.warning(
                    stage="validation",
                    event="validation_failed",
                    message=validation["message"],
                    details={"reason": validation.get("reason")},
                )
                return ExecuteResult(
                    success=False,
                    generated_sql=sql,
                    validation_status=validation,
                    selected_tables=selected_names,
                    error=validation["message"],
                )

            logger.info(
                stage="validation",
                event="validation_passed",
                message="SQL passed read-only validation",
            )

            exec_result = execute_readonly_sql(
                prepare.engine,
                sql,
                max_rows=self.settings.execution.max_result_rows,
                timeout_sec=self.settings.execution.query_timeout_sec,
                logger=logger,
            )

            result_meta: dict[str, Any] = {
                "row_count": exec_result.row_count,
                "duration_ms": round(exec_result.duration_ms, 1),
                "truncated": exec_result.truncated,
                "pipeline_duration_ms": round((time.perf_counter() - render_start) * 1000, 1),
            }

            logger.info(stage="render", event="render_complete", message="Execute pipeline complete", details=result_meta)

            return ExecuteResult(
                success=True,
                generated_sql=sql,
                validation_status=validation,
                result_df=exec_result.dataframe,
                result_meta=result_meta,
                selected_tables=selected_names,
            )

        except Exception as exc:
            logger.error(
                stage="pipeline",
                event="pipeline_failed",
                message="Execute pipeline failed",
                details={"error": str(exc)},
            )
            return ExecuteResult(
                success=False,
                generated_sql=sql,
                selected_tables=selected_names,
                error=str(exc),
            )
