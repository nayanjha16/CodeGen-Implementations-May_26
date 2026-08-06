"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=database | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DatabaseConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class DatabaseConfigBuilder:
    def __init__(self) -> None:
        self._name = "database"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "DatabaseConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "DatabaseConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "DatabaseConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> DatabaseConfig:
        return DatabaseConfig(self._name, self._limit, self._enabled)
