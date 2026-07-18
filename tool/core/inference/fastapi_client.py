"""FastAPI OpenAI-compatible inference client."""

from __future__ import annotations

from typing import Any

import httpx

from tool.core.activity_logger import ActivityLogger
from tool.core.settings_store import FastApiSettings
from tool.core.sql_extractor import extract_sql


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
        payload: dict[str, Any] = {
            "model": self.config.model,
            "intent": self.config.intent,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        if self.logger:
            self.logger.info(
                stage="inference",
                event="fastapi_request_start",
                message="Sending prompt to FastAPI inference endpoint",
                details={"model": self.config.model, "intent": self.config.intent},
            )

        try:
            with httpx.Client(timeout=self.config.timeout_sec) as client:
                response = client.post(self._chat_url(), json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError(format_timeout_error(exc, self.config.timeout_sec)) from exc

        content = data["choices"][0]["message"]["content"]
        sql = extract_sql(content)

        if self.logger:
            self.logger.info(
                stage="inference",
                event="sql_generated",
                message="SQL extracted from API response",
                details={"sql": sql, "sql_length": len(sql), "raw_length": len(content)},
            )

        return sql
