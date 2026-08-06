"""DesignPatternsSolid | kind=design_pattern | label=proxy | domain=discount | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountService(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class DiscountRealService(DiscountService):
    def load(self, id: str) -> str:
        return f"real-discount:{id}"

class DiscountProxy(DiscountService):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: DiscountRealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = DiscountRealService()
        return self._real.load(id)
