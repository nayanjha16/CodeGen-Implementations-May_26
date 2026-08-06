"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=streaming | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StreamingConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class StreamingConfigBuilder:
    def __init__(self) -> None:
        self._name = "streaming"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "StreamingConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "StreamingConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "StreamingConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> StreamingConfig:
        return StreamingConfig(self._name, self._limit, self._enabled)
