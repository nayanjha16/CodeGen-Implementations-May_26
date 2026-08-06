"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=sensors | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class SensorsRealService(SensorsService):
    def load(self, id: str) -> str:
        return f"real-sensors:{id}"

class SensorsProxy(SensorsService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: SensorsRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = SensorsRealService()
        return self._real.load(id)
