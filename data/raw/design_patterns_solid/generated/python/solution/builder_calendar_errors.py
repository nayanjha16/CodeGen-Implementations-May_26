"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=calendar | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CalendarConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class CalendarConfigBuilder:
    def __init__(self) -> None:
        self._name = "calendar"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "CalendarConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "CalendarConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "CalendarConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> CalendarConfig:
        return CalendarConfig(self._name, self._limit, self._enabled)
