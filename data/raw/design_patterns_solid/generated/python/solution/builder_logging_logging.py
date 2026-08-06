"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=logging | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class LoggingConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class LoggingConfigBuilder:
    def __init__(self) -> None:
        self._name = "logging"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "LoggingConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "LoggingConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "LoggingConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> LoggingConfig:
        return LoggingConfig(self._name, self._limit, self._enabled)
