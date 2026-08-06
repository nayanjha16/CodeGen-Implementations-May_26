"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=logging | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class LoggingRealService(LoggingService):
    def load(self, id: str) -> str:
        return f"real-logging:{id}"

class LoggingProxy(LoggingService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: LoggingRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = LoggingRealService()
        return self._real.load(id)
