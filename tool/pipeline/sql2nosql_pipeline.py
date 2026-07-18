"""End-to-end SQL-to-NoSQL Execute pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy.engine import Engine

from src.documentation.prompt_builder import DocumentationPromptBuilder
from src.sql2nosql.prompt_builder import NoSQLPromptBuilder
from src.utils.schema_conversion import derive_mongo_schema_json

from tool.adapters.base import ExecuteResult
from tool.core.activity_logger import ActivityLogger
from tool.core.database import get_active_engine
from tool.core.inference.fastapi_client import FastApiInferenceClient
from tool.core.mongo_database import get_active_mongo_client
from tool.core.mongo_executor import execute_mongo_query, validate_mongo_query
from tool.core.safety_validator import SafetyValidator
from tool.core.schema_loader import TableSchema, load_all_tables
from tool.core.schema_selector import SchemaSelectionResult, build_schema_ddl, select_tables_for_prompt
from tool.core.settings_store import AppSettings, DatabaseConnection, SettingsStore


@dataclass
class Sql2NoSqlPrepareResult:
    """Connection + schema state after auto table selection, before user confirmation."""

    engine: Engine
    conn: DatabaseConnection
    all_tables: list[TableSchema]
    selection: SchemaSelectionResult
    sql_query: str


class Sql2NoSqlPipeline:
    """Orchestrate connect → schema → inference → validate → execute → document."""

    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or SettingsStore().load()
        self.prompt_builder = NoSQLPromptBuilder()
        self.doc_prompt_builder = DocumentationPromptBuilder()
        self.validator = SafetyValidator()

    def prepare(self, sql_query: str, *, logger: ActivityLogger) -> Sql2NoSqlPrepareResult | ExecuteResult:
        """Connect, validate SQL, load schema, and suggest relevant tables."""
        sql_query = sql_query.strip()
        if not sql_query:
            return ExecuteResult(success=False, error="Please enter a SQL query.")

        validation = self.validator.validate(sql_query)
        if not validation["passed"]:
            logger.warning(
                stage="validation",
                event="validation_failed",
                message=validation["message"],
                details={"reason": validation.get("reason")},
            )
            return ExecuteResult(
                success=False,
                generated_sql=sql_query,
                validation_status=validation,
                error=validation["message"],
            )

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

        try:
            mongo_client, mongo_conn = get_active_mongo_client(self.settings)
            mongo_client.admin.command("ping")
            logger.info(
                stage="connection",
                event="mongo_connection_established",
                message="Connected to MongoDB",
                details={"connection": mongo_conn.name, "database": mongo_conn.database},
            )
        except Exception as exc:
            logger.error(
                stage="connection",
                event="mongo_connection_failed",
                message="Failed to connect to MongoDB",
                details={"error": str(exc)},
            )
            return ExecuteResult(success=False, error=str(exc))

        logger.info(stage="render", event="render_start", message="Starting schema selection for SQL-to-NoSQL")

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
                sql_query,
                all_tables,
                embedding_model=self.settings.schema_selection.embedding_model,
                top_k=self.settings.schema_selection.top_k,
                min_score=self.settings.schema_selection.min_score,
                logger=logger,
            )
            return Sql2NoSqlPrepareResult(
                engine=engine,
                conn=conn,
                all_tables=all_tables,
                selection=selection,
                sql_query=sql_query,
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
        sql_query: str,
        prepare: Sql2NoSqlPrepareResult,
        selected_names: list[str],
        *,
        logger: ActivityLogger,
    ) -> ExecuteResult:
        """Generate NoSQL, execute on MongoDB, then generate documentation."""
        sql_query = sql_query.strip()
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
        nosql_schema = derive_mongo_schema_json(schema_ddl)
        render_start = time.perf_counter()
        nosql: str | None = None
        documentation: str | None = None

        try:
            prompt = self.prompt_builder.build(sql_query, schema_ddl, nosql_schema=nosql_schema)
            logger.info(
                stage="prompt",
                event="prompt_built",
                message="Built SQL-to-NoSQL prompt with selected schema",
                details={"prompt_length": len(prompt), "tables": selected_names},
            )
            logger.info(
                stage="prompt",
                event="prompt_body",
                message="Full prompt payload",
                details={"prompt": prompt},
            )

            client = FastApiInferenceClient(self.settings.fastapi, logger=logger)
            nosql = client.generate_nosql(prompt)
            if not nosql:
                logger.error(
                    stage="inference",
                    event="nosql_generation_failed",
                    message="Could not extract NoSQL from API response",
                )
                return ExecuteResult(
                    success=False,
                    generated_sql=sql_query,
                    selected_tables=selected_names,
                    error="Could not extract MongoDB query from model response.",
                )

            logger.info(stage="validation", event="validation_start", message="Validating generated NoSQL")
            validation = validate_mongo_query(nosql)
            if not validation["passed"]:
                logger.warning(
                    stage="validation",
                    event="validation_failed",
                    message=validation["message"],
                    details={"reason": validation.get("reason")},
                )
                return ExecuteResult(
                    success=False,
                    generated_sql=sql_query,
                    generated_nosql=nosql,
                    validation_status=validation,
                    selected_tables=selected_names,
                    error=validation["message"],
                )

            logger.info(
                stage="validation",
                event="validation_passed",
                message="NoSQL passed syntax validation",
            )

            mongo_client, mongo_conn = get_active_mongo_client(self.settings)
            db = mongo_client[mongo_conn.database]
            exec_result = execute_mongo_query(
                db,
                nosql,
                max_rows=self.settings.execution.max_result_rows,
                max_time_ms=self.settings.execution.query_timeout_sec * 1000,
                logger=logger,
            )
            if exec_result.error:
                return ExecuteResult(
                    success=False,
                    generated_sql=sql_query,
                    generated_nosql=nosql,
                    validation_status=validation,
                    selected_tables=selected_names,
                    error=exec_result.error,
                )

            doc_prompt = self.doc_prompt_builder.build(
                nosql,
                schema=schema_ddl,
                nosql_schema=nosql_schema,
            )
            logger.info(
                stage="prompt",
                event="doc_prompt_built",
                message="Built documentation prompt",
                details={"prompt_length": len(doc_prompt)},
            )
            logger.info(
                stage="prompt",
                event="doc_prompt_body",
                message="Full documentation prompt payload",
                details={"prompt": doc_prompt},
            )
            logger.info(
                stage="inference",
                event="documentation_start",
                message="Sending documentation prompt to FastAPI",
                details={"intent": "nosql2doc", "prompt_length": len(doc_prompt)},
            )
            documentation = client.generate_documentation(doc_prompt)
            if documentation:
                logger.info(
                    stage="inference",
                    event="documentation_ready",
                    message="Documentation generated",
                    details={"documentation": documentation},
                )

            result_meta: dict[str, Any] = {
                "row_count": exec_result.row_count,
                "duration_ms": round(exec_result.duration_ms, 1),
                "truncated": exec_result.truncated,
                "pipeline_duration_ms": round((time.perf_counter() - render_start) * 1000, 1),
            }

            logger.info(
                stage="render",
                event="render_complete",
                message="SQL-to-NoSQL pipeline complete",
                details=result_meta,
            )

            return ExecuteResult(
                success=True,
                generated_sql=sql_query,
                generated_nosql=nosql,
                documentation=documentation,
                validation_status=validation,
                result_df=exec_result.dataframe,
                result_meta=result_meta,
                selected_tables=selected_names,
            )

        except Exception as exc:
            logger.error(
                stage="pipeline",
                event="pipeline_failed",
                message="SQL-to-NoSQL pipeline failed",
                details={"error": str(exc)},
            )
            return ExecuteResult(
                success=False,
                generated_sql=sql_query,
                generated_nosql=nosql,
                documentation=documentation,
                selected_tables=selected_names,
                error=str(exc),
            )
