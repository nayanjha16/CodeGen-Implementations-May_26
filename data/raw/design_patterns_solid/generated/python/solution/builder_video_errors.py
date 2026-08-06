"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=video | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class VideoConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class VideoConfigBuilder:
    def __init__(self) -> None:
        self._name = "video"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "VideoConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "VideoConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "VideoConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> VideoConfig:
        return VideoConfig(self._name, self._limit, self._enabled)
