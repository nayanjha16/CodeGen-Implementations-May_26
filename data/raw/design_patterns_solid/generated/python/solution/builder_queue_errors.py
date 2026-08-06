"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=queue | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class QueueConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class QueueConfigBuilder:
    def __init__(self) -> None:
        self._name = "queue"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "QueueConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "QueueConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "QueueConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> QueueConfig:
        return QueueConfig(self._name, self._limit, self._enabled)
