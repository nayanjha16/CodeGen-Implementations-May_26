"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=backup | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BackupConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class BackupConfigBuilder:
    def __init__(self) -> None:
        self._name = "backup"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "BackupConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "BackupConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "BackupConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> BackupConfig:
        return BackupConfig(self._name, self._limit, self._enabled)
