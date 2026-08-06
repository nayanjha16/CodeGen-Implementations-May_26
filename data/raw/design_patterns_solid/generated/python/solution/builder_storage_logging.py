"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=storage | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StorageConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class StorageConfigBuilder:
    def __init__(self) -> None:
        self._name = "storage"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "StorageConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "StorageConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "StorageConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> StorageConfig:
        return StorageConfig(self._name, self._limit, self._enabled)
