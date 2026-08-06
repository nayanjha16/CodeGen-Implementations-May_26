"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class MetricsRealService(MetricsService):
    def load(self, id: str) -> str:
        return f"real-metrics:{id}"

class MetricsProxy(MetricsService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: MetricsRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = MetricsRealService()
        return self._real.load(id)
