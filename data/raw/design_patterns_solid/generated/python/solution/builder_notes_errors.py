"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=notes | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotesConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class NotesConfigBuilder:
    def __init__(self) -> None:
        self._name = "notes"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "NotesConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "NotesConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "NotesConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> NotesConfig:
        return NotesConfig(self._name, self._limit, self._enabled)
