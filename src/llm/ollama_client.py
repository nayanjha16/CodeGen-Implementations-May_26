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

    def is_available(self) -> bool:
        """Return True when the Ollama server responds to a health check."""
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=min(self.timeout, 5.0))
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def list_model_names(self) -> list[str]:
        """Return model names reported by Ollama, or an empty list when unavailable."""
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.debug("Failed to list Ollama models from %s: %s", url, exc)
            return []

        data = response.json()
        models = data.get("models") or []
        names: list[str] = []
        for entry in models:
            if isinstance(entry, dict):
                name = entry.get("name")
                if isinstance(name, str) and name.strip():
                    names.append(name.strip())
        return names

    def has_model(self, model: str) -> bool:
        """Return True when ``model`` (or a matching tag) is available in Ollama."""
        requested = model.strip().lower()
        if not requested:
            return False

        available = self.list_model_names()
        if not available:
            return False

        requested_base = requested.split(":", 1)[0]
        for name in available:
            normalized = name.strip().lower()
            if normalized == requested:
                return True
            if normalized.split(":", 1)[0] == requested_base:
                return True
        return False

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
