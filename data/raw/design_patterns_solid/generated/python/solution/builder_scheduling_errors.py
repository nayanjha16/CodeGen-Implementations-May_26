"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=scheduling | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SchedulingConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class SchedulingConfigBuilder:
    def __init__(self) -> None:
        self._name = "scheduling"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "SchedulingConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "SchedulingConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "SchedulingConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> SchedulingConfig:
        return SchedulingConfig(self._name, self._limit, self._enabled)
