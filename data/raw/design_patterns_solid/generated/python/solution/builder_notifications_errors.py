"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=notifications | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class NotificationsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class NotificationsConfigBuilder:
    def __init__(self) -> None:
        self._name = "notifications"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "NotificationsConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "NotificationsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "NotificationsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> NotificationsConfig:
        return NotificationsConfig(self._name, self._limit, self._enabled)
