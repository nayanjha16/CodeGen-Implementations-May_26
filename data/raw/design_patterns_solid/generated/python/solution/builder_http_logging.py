"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=http | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class HttpConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class HttpConfigBuilder:
    def __init__(self) -> None:
        self._name = "http"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "HttpConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "HttpConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "HttpConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> HttpConfig:
        return HttpConfig(self._name, self._limit, self._enabled)
