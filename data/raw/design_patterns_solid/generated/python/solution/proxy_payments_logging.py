"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=payments | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class PaymentsRealService(PaymentsService):
    def load(self, id: str) -> str:
        return f"real-payments:{id}"

class PaymentsProxy(PaymentsService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: PaymentsRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = PaymentsRealService()
        return self._real.load(id)
