"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=map | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class MapConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class MapConfigBuilder:
    def __init__(self) -> None:
        self._name = "map"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "MapConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "MapConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "MapConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> MapConfig:
        return MapConfig(self._name, self._limit, self._enabled)
