"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=cache | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CacheConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class CacheConfigBuilder:
    def __init__(self) -> None:
        self._name = "cache"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "CacheConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "CacheConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "CacheConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> CacheConfig:
        return CacheConfig(self._name, self._limit, self._enabled)
