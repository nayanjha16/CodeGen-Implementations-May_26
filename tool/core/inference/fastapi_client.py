"""FastAPI OpenAI-compatible inference client."""

from __future__ import annotations

from typing import Any, Callable

import httpx

from tool.core.activity_logger import ActivityLogger
from tool.core.settings_store import FastApiSettings
from tool.core.sql_extractor import extract_sql
from tool.core.nosql_extractor import extract_nosql
from tool.core.doc_extractor import extract_documentation


def format_timeout_error(exc: Exception, timeout_sec: int) -> str:
    """Include configured timeout when httpx reports a read timeout."""
    message = str(exc)
    if isinstance(exc, httpx.TimeoutException) or "read operation timed out" in message.lower():
        return f"{message} (timeout: {timeout_sec} sec)"
    return message


class FastApiInferenceClient:
    """Call hf-deploy /v1/chat/completions and extract SQL from response."""

    def __init__(self, config: FastApiSettings, logger: ActivityLogger | None = None):
        self.config = config
        self.logger = logger

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _chat_url(self) -> str:
        base = self.config.base_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    def generate_sql(self, prompt: str) -> str:
        return self.generate_text(prompt, intent=self.config.intent or "text2sql", extractor=extract_sql)

    def generate_nosql(self, prompt: str) -> str:
        return self.generate_text(prompt, intent="sql2nosql", extractor=extract_nosql)

    def generate_documentation(self, prompt: str) -> str:
        return self.generate_text(prompt, intent="nosql2doc", extractor=extract_documentation)

    def generate_text(
        self,
        prompt: str,
        *,
        intent: str,
        extractor: Callable[[str], str],
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "intent": intent,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        if self.logger:
            self.logger.info(
                stage="inference",
                event="fastapi_request_start",
                message="Sending prompt to FastAPI inference endpoint",
                details={"model": self.config.model, "intent": intent},
            )

        try:
            with httpx.Client(timeout=self.config.timeout_sec) as client:
                response = client.post(self._chat_url(), json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError(format_timeout_error(exc, self.config.timeout_sec)) from exc

        content = data["choices"][0]["message"]["content"]
        extracted = extractor(content)

        if self.logger:
            details: dict[str, Any] = {"raw_length": len(content), "intent": intent}
            if intent == "text2sql":
                details.update({"sql": extracted, "sql_length": len(extracted)})
                event = "sql_generated"
                message = "SQL extracted from API response"
            elif intent == "sql2nosql":
                details.update({"nosql": extracted, "nosql_length": len(extracted)})
                event = "nosql_generated"
                message = "NoSQL extracted from API response"
            else:
                details.update({"documentation": extracted, "doc_length": len(extracted)})
                event = "documentation_generated"
                message = "Documentation extracted from API response"
            self.logger.info(
                stage="inference",
                event=event,
                message=message,
                details=details,
            )

        return extracted
