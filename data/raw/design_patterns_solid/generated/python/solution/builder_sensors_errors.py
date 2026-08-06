"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=sensors | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SensorsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class SensorsConfigBuilder:
    def __init__(self) -> None:
        self._name = "sensors"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "SensorsConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "SensorsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "SensorsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> SensorsConfig:
        return SensorsConfig(self._name, self._limit, self._enabled)
