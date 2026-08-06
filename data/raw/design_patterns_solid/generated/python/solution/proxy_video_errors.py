"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=video | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class VideoRealService(VideoService):
    def load(self, id: str) -> str:
        return f"real-video:{id}"

class VideoProxy(VideoService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: VideoRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = VideoRealService()
        return self._real.load(id)
