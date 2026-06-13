"""Translator interface: the contract every backend implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TranslationTask:
    description: str                  # English description (always present)
    python_code: str | None = None    # if set -> Python->Rust mode, else English->Rust mode
    signature: str | None = None      # optional Rust fn signature to target
    context_examples: list[str] = field(default_factory=list)  # filled by RAG


class Translator(ABC):
    @abstractmethod
    def generate(self, task: TranslationTask) -> str:
        """Return Rust source code for the given task."""
