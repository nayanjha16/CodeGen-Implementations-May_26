"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=widgets | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class WidgetsRealService(WidgetsService):
    def load(self, id: str) -> str:
        return f"real-widgets:{id}"

class WidgetsProxy(WidgetsService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: WidgetsRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = WidgetsRealService()
        return self._real.load(id)
