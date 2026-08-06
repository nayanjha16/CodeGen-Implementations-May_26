"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=scheduling | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SchedulingRealService(SchedulingService):
    def load(self, id: str) -> str:
        return f"real-scheduling:{id}"

class SchedulingProxy(SchedulingService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SchedulingRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SchedulingRealService()
        return self._real.load(id)
