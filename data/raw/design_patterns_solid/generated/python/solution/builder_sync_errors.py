"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=sync | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SyncConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class SyncConfigBuilder:
    def __init__(self) -> None:
        self._name = "sync"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "SyncConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "SyncConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "SyncConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> SyncConfig:
        return SyncConfig(self._name, self._limit, self._enabled)
