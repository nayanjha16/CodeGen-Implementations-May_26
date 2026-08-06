"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=feed | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class FeedConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class FeedConfigBuilder:
    def __init__(self) -> None:
        self._name = "feed"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "FeedConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "FeedConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "FeedConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> FeedConfig:
        return FeedConfig(self._name, self._limit, self._enabled)
