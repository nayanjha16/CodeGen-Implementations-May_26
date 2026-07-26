"""Execute agent plans — tool orchestration with SQL retry (FR-5)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.clients.orchestrator_llm import OrchestratorLLM
from agent.config.settings import AgentSettings, get_settings
from agent.database.postgres import PostgresExecutor
from agent.lib.sql_repair import repair_listing_select
from agent.lib.sql_validation import normalize_generated_sql, validate_sql_for_execution
from agent.lib.text2sql_hints import augment_codegen_question, format_deterministic_summary, format_listing_summary
from agent.orchestration.state import AgentResult, RunContext
from agent.orchestrator.intent_detector import (
    IntentDetector,
    extract_mongo_from_message,
    extract_sql_from_message,
)
from agent.orchestrator.planner import PlanStep, build_plan
from agent.orchestrator.retry import RetryState, should_retry_sql
from agent.tools.execution_tool import ExecutionTool
from agent.tools.fastapi_tool import FastApiTool
from agent.tools.schema_tool import SchemaTool


@dataclass
class AgentRunner:
    """Run one user turn through tools + orchestrator LLM."""

    settings: AgentSettings | None = None
    detector: IntentDetector | None = None
    llm: OrchestratorLLM | None = None
    schema_tool: SchemaTool | None = None
    fastapi_tool: FastApiTool | None = None
    execution_tool: ExecutionTool | None = None
    postgres: PostgresExecutor | None = None

    def __post_init__(self) -> None:
        cfg = self.settings or get_settings()
        self.settings = cfg
        self.detector = self.detector or IntentDetector(cfg)
        self.llm = self.llm or OrchestratorLLM(cfg)
        self.schema_tool = self.schema_tool or SchemaTool(cfg)
        self.fastapi_tool = self.fastapi_tool or FastApiTool(cfg)
        self.execution_tool = self.execution_tool or ExecutionTool(cfg)
        self.postgres = self.postgres or PostgresExecutor(cfg)

    def close(self) -> None:
        self.schema_tool.close()
        self.execution_tool.close()
        self.postgres.close()

    def __enter__(self) -> AgentRunner:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def run(
        self,
        user_message: str,
        *,
        explicit_intent: str | None = None,
        db_id: str | None = None,
        dataset: str | None = None,
        sql: str | None = None,
    ) -> AgentResult:
        intent_result = self.detector.detect(
            user_message,
            explicit_intent=explicit_intent,
        )
        plan = build_plan(intent_result.intent)
        ctx = RunContext(
            user_message=user_message,
            db_id=db_id,
            dataset=dataset,
            intent=intent_result.intent,
            sql=(sql or extract_sql_from_message(user_message) or "").strip(),
            mongo_query=(extract_mongo_from_message(user_message) or "").strip(),
        )

        for step in plan.steps:
            if step == PlanStep.SUMMARIZE:
                break
            self._run_step(ctx, step)

        answer = self._summarize(ctx)
        return AgentResult(
            answer=answer,
            intent=ctx.intent,
            sql=ctx.sql,
            mongo_query=ctx.mongo_query,
            documentation=ctx.documentation,
            rows=ctx.rows,
            error=ctx.error,
        )

    def _run_step(self, ctx: RunContext, step: PlanStep) -> None:
        if step == PlanStep.EXTRACT_SCHEMA:
            self._extract_schema(ctx)
        elif step == PlanStep.GENERATE_SQL:
            self._generate_sql(ctx)
        elif step == PlanStep.VALIDATE_SQL:
            self._validate_sql(ctx)
        elif step == PlanStep.EXECUTE_POSTGRES:
            self._execute_postgres(ctx)
        elif step == PlanStep.GENERATE_NOSQL:
            self._ensure_schema(ctx)
            self._generate_nosql(ctx)
        elif step == PlanStep.EXECUTE_MONGO:
            self._execute_mongo(ctx)
        elif step == PlanStep.GENERATE_DOCUMENTATION:
            self._ensure_schema(ctx)
            self._generate_documentation(ctx)
        elif step == PlanStep.EXPLAIN_SQL:
            self._explain_sql(ctx)

    def _extract_schema(self, ctx: RunContext) -> None:
        result = self.schema_tool.extract(
            ctx.user_message,
            db_id=ctx.db_id,
            dataset=ctx.dataset,
        )
        ctx.schema_ddl = result.schema_ddl
        ctx.nosql_schema = result.nosql_schema
        ctx.allowed_tables = set(result.tables)

    def _ensure_schema(self, ctx: RunContext) -> None:
        if ctx.schema_ddl.strip():
            return
        snapshot = self.postgres.introspect_schema(
            db_id=ctx.db_id,
            dataset=ctx.dataset,
        )
        ctx.schema_ddl = snapshot.to_ddl()
        ctx.allowed_tables = {table.name for table in snapshot.tables}
        from src.utils.schema_conversion import derive_mongo_schema_json

        ctx.nosql_schema = derive_mongo_schema_json(ctx.schema_ddl)

    def _generate_sql(self, ctx: RunContext) -> None:
        if not ctx.schema_ddl:
            self._extract_schema(ctx)
        question = augment_codegen_question(
            ctx.user_message,
            ctx.allowed_tables or None,
        )
        ctx.sql = self.fastapi_tool.generate_sql(
            question,
            ctx.schema_ddl,
        )
        if ctx.schema_ddl:
            ctx.sql = normalize_generated_sql(ctx.sql, ctx.schema_ddl, ctx.user_message)
            ctx.sql = repair_listing_select(ctx.sql, ctx.user_message)

    @staticmethod
    def _retry_question(ctx: RunContext, question: str) -> str:
        return augment_codegen_question(question, ctx.allowed_tables or None)

    def _normalize_sql(self, ctx: RunContext) -> None:
        if ctx.sql and ctx.schema_ddl:
            ctx.sql = normalize_generated_sql(ctx.sql, ctx.schema_ddl, ctx.user_message)
            ctx.sql = repair_listing_select(ctx.sql, ctx.user_message)

    def _validate_sql(self, ctx: RunContext) -> None:
        if not ctx.sql:
            ctx.sql = extract_sql_from_message(ctx.user_message) or ctx.user_message.strip()
        allowed = ctx.allowed_tables or None
        if ctx.intent == "validate_sql" and not ctx.allowed_tables and not ctx.schema_ddl:
            self._ensure_schema(ctx)
            allowed = ctx.allowed_tables or None
        ctx.validation_message = validate_sql_for_execution(
            ctx.sql,
            allowed_tables=allowed,
        )

    def _execute_postgres(self, ctx: RunContext) -> None:
        if not ctx.sql:
            self._generate_sql(ctx)

        retry = RetryState.from_settings(self.settings)
        allowed = ctx.allowed_tables or None

        while True:
            self._normalize_sql(ctx)
            validation_error = validate_sql_for_execution(ctx.sql, allowed_tables=allowed)
            if validation_error:
                ctx.error = validation_error
                if should_retry_sql(retry, success=False):
                    retry.record_failure(sql=ctx.sql, error=validation_error)
                    ctx.sql = self.fastapi_tool.generate_sql(
                        self._retry_question(ctx, ctx.user_message),
                        ctx.schema_ddl,
                        previous_sql=ctx.sql,
                        db_error=validation_error,
                    )
                    self._normalize_sql(ctx)
                    continue
                return

            result = self.execution_tool.run(
                ctx.sql,
                engine="postgres",
                db_id=ctx.db_id,
                dataset=ctx.dataset,
                allowed_tables=allowed,
            )
            if result.success:
                ctx.rows = result.rows
                ctx.error = None
                return

            ctx.error = result.error
            if should_retry_sql(retry, success=False):
                retry.record_failure(sql=ctx.sql, error=result.error or "execution failed")
                ctx.sql = self.fastapi_tool.generate_sql(
                    self._retry_question(ctx, ctx.user_message),
                    ctx.schema_ddl,
                    previous_sql=ctx.sql,
                    db_error=result.error or "execution failed",
                )
                self._normalize_sql(ctx)
                continue
            return

    def _generate_nosql(self, ctx: RunContext) -> None:
        if not ctx.sql:
            raise ValueError("sql2nosql requires SQL in the message or via --sql")
        ctx.mongo_query = self.fastapi_tool.generate_nosql(
            ctx.sql,
            ctx.schema_ddl,
            nosql_schema=ctx.nosql_schema or None,
        )

    def _execute_mongo(self, ctx: RunContext) -> None:
        if not ctx.mongo_query:
            self._generate_nosql(ctx)
        result = self.execution_tool.run(
            ctx.mongo_query,
            engine="mongo",
            db_id=ctx.db_id,
            dataset=ctx.dataset,
        )
        if result.success:
            ctx.rows = result.rows
            ctx.error = None
        else:
            ctx.error = result.error

    def _generate_documentation(self, ctx: RunContext) -> None:
        if not ctx.mongo_query:
            ctx.mongo_query = extract_mongo_from_message(ctx.user_message) or ""
        if not ctx.mongo_query:
            raise ValueError("nosql2doc requires a MongoDB shell query in the message")
        ctx.documentation = self.fastapi_tool.generate_documentation(
            ctx.mongo_query,
            schema=ctx.schema_ddl,
            nosql_schema=ctx.nosql_schema or None,
            question=ctx.user_message,
        )

    def _explain_sql(self, ctx: RunContext) -> None:
        if not ctx.sql:
            ctx.sql = extract_sql_from_message(ctx.user_message) or ""
        if not ctx.sql:
            raise ValueError("explain_sql requires SQL in the message or via --sql")
        if not ctx.schema_ddl:
            self._extract_schema(ctx)
        ctx.explanation = self.llm.explain_sql(ctx.sql, schema=ctx.schema_ddl)

    def _summarize(self, ctx: RunContext) -> str:
        if ctx.intent == "validate_sql":
            if ctx.validation_message:
                return f"The SQL is not valid: {ctx.validation_message}"
            return "The SQL passed validation checks and is safe to run."

        if ctx.intent == "nosql2doc" and ctx.documentation:
            return ctx.documentation

        if ctx.intent == "explain_sql" and ctx.explanation:
            return ctx.explanation

        deterministic = format_deterministic_summary(
            question=ctx.user_message,
            rows=ctx.rows,
            error=ctx.error,
        )
        if deterministic is not None:
            return deterministic

        listing = format_listing_summary(
            question=ctx.user_message,
            rows=ctx.rows,
            error=ctx.error,
        )
        if listing is not None:
            return listing

        query = ctx.mongo_query or ctx.sql
        return self.llm.summarize_results(
            question=ctx.user_message,
            query=query,
            rows=ctx.rows,
            error=ctx.error,
        )
