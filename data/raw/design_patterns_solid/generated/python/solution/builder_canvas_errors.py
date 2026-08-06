"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=canvas | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CanvasConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class CanvasConfigBuilder:
    def __init__(self) -> None:
        self._name = "canvas"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "CanvasConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "CanvasConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "CanvasConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> CanvasConfig:
        return CanvasConfig(self._name, self._limit, self._enabled)
