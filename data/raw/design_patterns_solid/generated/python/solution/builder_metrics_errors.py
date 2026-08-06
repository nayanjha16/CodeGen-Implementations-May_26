"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=metrics | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class MetricsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class MetricsConfigBuilder:
    def __init__(self) -> None:
        self._name = "metrics"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "MetricsConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "MetricsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "MetricsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> MetricsConfig:
        return MetricsConfig(self._name, self._limit, self._enabled)
