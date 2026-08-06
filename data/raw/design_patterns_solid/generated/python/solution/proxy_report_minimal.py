"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=report | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ReportService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class ReportRealService(ReportService):
    def load(self, id: str) -> str:
        return f"real-report:{id}"

class ReportProxy(ReportService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: ReportRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = ReportRealService()
        return self._real.load(id)
