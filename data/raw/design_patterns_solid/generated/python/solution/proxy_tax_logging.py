"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=tax | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class TaxRealService(TaxService):
    def load(self, id: str) -> str:
        return f"real-tax:{id}"

class TaxProxy(TaxService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: TaxRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = TaxRealService()
        return self._real.load(id)
