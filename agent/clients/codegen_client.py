"""HTTP client for CodeGen API on Cloud Run (OpenAI-compatible + intent routing)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import httpx

from agent.config.settings import AgentSettings, get_settings
from agent.lib.output_extract import (
    extract_documentation,
    extract_nosql,
    extract_sql,
)

IntentKind = Literal["text2sql", "sql2nosql", "nosql2doc"]


@dataclass(frozen=True)
class CodeGenHealth:
    ok: bool
    status_code: int
    body: dict[str, Any] | None = None
    error: str | None = None


class CodeGenClient:
    """Call /v1/chat/completions with training-aligned prompts from src/."""

    def __init__(self, settings: AgentSettings | None = None) -> None:
        self._settings = settings or get_settings()
        from src.sql2nosql.prompt_builder import NoSQLPromptBuilder
        from src.text2sql.prompt_builder import PromptBuilder

        from agent.lib.src_imports import documentation_prompt_builder_class

        self._text2sql_prompts = PromptBuilder()
        self._sql2nosql_prompts = NoSQLPromptBuilder()
        self._doc_prompts = documentation_prompt_builder_class()()

    def _chat_url(self) -> str:
        base = self._settings.codegen_api_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def _health_url(self) -> str:
        base = self._settings.codegen_api_url.rstrip("/")
        if base.endswith("/v1"):
            return base[: -len("/v1")] + "/health"
        return f"{base}/health"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._settings.codegen_api_key:
            headers["Authorization"] = f"Bearer {self._settings.codegen_api_key}"
        return headers

    def _post_chat(self, prompt: str, intent: IntentKind) -> str:
        payload: dict[str, Any] = {
            "model": self._settings.codegen_model,
            "intent": intent,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self._settings.codegen_temperature,
            "max_tokens": self._settings.codegen_max_tokens,
        }
        timeout = self._settings.codegen_timeout_sec
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    self._chat_url(),
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"{exc} (timeout: {timeout} sec)") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip()
            raise RuntimeError(
                f"CodeGen API error {exc.response.status_code}: {detail[:500]}"
            ) from exc

        content = data["choices"][0]["message"]["content"]
        if intent == "text2sql":
            return extract_sql(content)
        if intent == "sql2nosql":
            return extract_nosql(content)
        return extract_documentation(content)

    @staticmethod
    def _build_retry_question(
        question: str,
        *,
        previous_sql: str,
        db_error: str,
    ) -> str:
        return (
            f"{question.strip()}\n\n"
            f"Previous SQL:\n{previous_sql.strip()}\n\n"
            f"Database error:\n{db_error.strip()}\n\n"
            "Generate corrected SQL only."
        )

    def generate_sql(
        self,
        question: str,
        schema: str,
        *,
        previous_sql: str | None = None,
        db_error: str | None = None,
    ) -> str:
        prompt_question = question
        if previous_sql and db_error:
            prompt_question = self._build_retry_question(
                question,
                previous_sql=previous_sql,
                db_error=db_error,
            )
        prompt = self._text2sql_prompts.build(prompt_question, schema)
        return self._post_chat(prompt, "text2sql")

    def generate_nosql(
        self,
        sql_query: str,
        schema: str,
        *,
        nosql_schema: str | None = None,
    ) -> str:
        prompt = self._sql2nosql_prompts.build(sql_query, schema, nosql_schema=nosql_schema)
        return self._post_chat(prompt, "sql2nosql")

    def generate_documentation(
        self,
        mongodb_query: str,
        schema: str = "",
        *,
        nosql_schema: str | None = None,
        question: str = "",
    ) -> str:
        prompt = self._doc_prompts.build(
            mongodb_query,
            schema=schema,
            nosql_schema=nosql_schema,
            question=question,
        )
        return self._post_chat(prompt, "nosql2doc")

    def health(self) -> CodeGenHealth:
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(self._health_url(), headers=self._headers())
            body: dict[str, Any] | None
            try:
                parsed = response.json()
                body = parsed if isinstance(parsed, dict) else None
            except ValueError:
                body = None
            return CodeGenHealth(
                ok=response.status_code == 200,
                status_code=response.status_code,
                body=body,
            )
        except Exception as exc:  # noqa: BLE001
            return CodeGenHealth(ok=False, status_code=0, error=str(exc))
