"""Inference client protocol."""

from __future__ import annotations

from typing import Protocol


class InferenceClient(Protocol):
    """Generate SQL text from a full prompt via FastAPI."""

    def generate_sql(self, prompt: str) -> str: ...
