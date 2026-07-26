"""Ollama orchestrator client — wraps src OllamaClient with agent settings."""

from __future__ import annotations

import json
import re
from typing import Any

from agent.config.settings import AgentSettings, get_settings
from agent.orchestrator.prompts import (
    EXPLAIN_SQL_PROMPT,
    INTENT_DETECTION_PROMPT,
    SUMMARIZE_PROMPT,
    SYSTEM_PROMPT,
)
from src.llm.ollama_client import OllamaClient

_JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")


class OrchestratorLLM:
    """Local LLM for intent fallback, summaries, and SQL explanations."""

    def __init__(self, settings: AgentSettings | None = None, client: OllamaClient | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = client or OllamaClient(base_url=self._settings.ollama_base_url)

    @property
    def model(self) -> str:
        return self._settings.ollama_model

    def chat(
        self,
        user_message: str,
        *,
        system: str | None = None,
        format_json: bool = False,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user_message})
        return self._client.chat(self.model, messages, format_json=format_json)

    @staticmethod
    def _parse_json_object(text: str) -> dict[str, Any]:
        text = text.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        match = _JSON_OBJECT_RE.search(text)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        raise ValueError(f"Expected JSON object in model output: {text[:200]}")

    def classify_intent(self, user_message: str) -> tuple[str, float]:
        raw = self.chat(
            f"{INTENT_DETECTION_PROMPT}\n\nUser request:\n{user_message.strip()}",
            system=SYSTEM_PROMPT,
            format_json=True,
        )
        data = self._parse_json_object(raw)
        intent = str(data.get("intent", "")).strip().lower()
        confidence = float(data.get("confidence", 0.5))
        return intent, confidence

    def summarize_results(
        self,
        *,
        question: str,
        query: str = "",
        rows: list[dict[str, Any]] | None = None,
        error: str | None = None,
    ) -> str:
        preview = json.dumps((rows or [])[:5], default=str)
        if len(rows or []) > 5:
            preview = preview[:-1] + ", ...]"
        parts = [
            SUMMARIZE_PROMPT,
            f"\nQuestion:\n{question.strip()}",
        ]
        if query.strip():
            parts.append(f"\nQuery:\n{query.strip()}")
        if error:
            parts.append(f"\nError:\n{error.strip()}")
        else:
            parts.append(f"\nResults (sample):\n{preview}")
        return self.chat("\n".join(parts), system=SYSTEM_PROMPT).strip()

    def explain_sql(self, sql: str, *, schema: str = "") -> str:
        parts = [EXPLAIN_SQL_PROMPT, f"\nSQL:\n{sql.strip()}"]
        if schema.strip():
            parts.append(f"\nSchema context:\n{schema.strip()}")
        return self.chat("\n".join(parts), system=SYSTEM_PROMPT).strip()
