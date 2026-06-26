"""Sync client for local Ollama chat API."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger("codegen")

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 120.0


class OllamaClient:
    """Call Ollama POST /api/chat with stream disabled."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        self.base_url = (
            base_url
            or os.environ.get("OLLAMA_BASE_URL")
            or DEFAULT_BASE_URL
        ).rstrip("/")
        timeout_env = os.environ.get("OLLAMA_TIMEOUT")
        self.timeout = float(
            timeout if timeout is not None else timeout_env or DEFAULT_TIMEOUT
        )

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        format_json: bool = False,
        think: bool | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if format_json:
            payload["format"] = "json"
        if think is not None:
            payload["think"] = think

        url = f"{self.base_url}/api/chat"
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Ollama chat failed at {url} for model {model!r}: {exc}"
            ) from exc

        data = response.json()
        message = data.get("message") or {}
        content = message.get("content", "")
        if not isinstance(content, str):
            return str(content)
        return content
