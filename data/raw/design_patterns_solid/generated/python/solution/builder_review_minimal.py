"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=review | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReviewConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class ReviewConfigBuilder:
    def __init__(self) -> None:
        self._name = "review"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "ReviewConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "ReviewConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "ReviewConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> ReviewConfig:
        return ReviewConfig(self._name, self._limit, self._enabled)
