"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=streaming | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class StreamingRealService(StreamingService):
    def load(self, id: str) -> str:
        return f"real-streaming:{id}"

class StreamingProxy(StreamingService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: StreamingRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = StreamingRealService()
        return self._real.load(id)
