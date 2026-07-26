"""Tool 2 — CodeGen API generation (spec /generate/* via HTTP adapter)."""

from __future__ import annotations

from typing import Any

from agent.clients.codegen_client import CodeGenClient, CodeGenHealth
from agent.config.settings import AgentSettings, get_settings


class FastApiTool:
    """Thin wrapper over CodeGenClient matching agent.md Tool 2 method names."""

    def __init__(
        self,
        settings: AgentSettings | None = None,
        client: CodeGenClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client or CodeGenClient(self._settings)

    def generate_sql(
        self,
        question: str,
        schema: str,
        *,
        previous_sql: str | None = None,
        db_error: str | None = None,
    ) -> str:
        return self._client.generate_sql(
            question,
            schema,
            previous_sql=previous_sql,
            db_error=db_error,
        )

    def generate_nosql(
        self,
        sql_query: str,
        schema: str,
        *,
        nosql_schema: str | None = None,
    ) -> str:
        return self._client.generate_nosql(
            sql_query,
            schema,
            nosql_schema=nosql_schema,
        )

    def generate_documentation(
        self,
        mongodb_query: str,
        schema: str = "",
        *,
        nosql_schema: str | None = None,
        question: str = "",
    ) -> str:
        return self._client.generate_documentation(
            mongodb_query,
            schema=schema,
            nosql_schema=nosql_schema,
            question=question,
        )

    def generate_explanation(self, sql: str) -> str:
        """Reserved for orchestrator LLM (Stage 5) — not a LoRA task."""
        raise NotImplementedError(
            "SQL explanation is handled by the Ollama orchestrator in Stage 5, not CodeGen API."
        )

    def health(self) -> CodeGenHealth:
        return self._client.health()


def generate_sql(question: str, schema: str, **kwargs: Any) -> str:
    return FastApiTool().generate_sql(question, schema, **kwargs)


def generate_nosql(sql_query: str, schema: str, **kwargs: Any) -> str:
    return FastApiTool().generate_nosql(sql_query, schema, **kwargs)


def generate_documentation(mongodb_query: str, schema: str = "", **kwargs: Any) -> str:
    return FastApiTool().generate_documentation(mongodb_query, schema=schema, **kwargs)
