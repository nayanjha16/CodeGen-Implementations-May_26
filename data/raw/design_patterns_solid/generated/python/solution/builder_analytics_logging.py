"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=analytics | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AnalyticsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class AnalyticsConfigBuilder:
    def __init__(self) -> None:
        self._name = "analytics"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "AnalyticsConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "AnalyticsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "AnalyticsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> AnalyticsConfig:
        return AnalyticsConfig(self._name, self._limit, self._enabled)
