"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=session | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SessionConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class SessionConfigBuilder:
    def __init__(self) -> None:
        self._name = "session"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "SessionConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "SessionConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "SessionConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> SessionConfig:
        return SessionConfig(self._name, self._limit, self._enabled)
