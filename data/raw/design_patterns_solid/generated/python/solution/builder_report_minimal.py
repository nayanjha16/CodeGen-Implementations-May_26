"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=report | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReportConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class ReportConfigBuilder:
    def __init__(self) -> None:
        self._name = "report"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "ReportConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "ReportConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "ReportConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> ReportConfig:
        return ReportConfig(self._name, self._limit, self._enabled)
