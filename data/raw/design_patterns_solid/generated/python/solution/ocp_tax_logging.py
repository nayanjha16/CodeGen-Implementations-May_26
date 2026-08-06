"""DesignPatternsSolid | kind=solid | label=ocp | domain=tax | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class TaxNoDiscount(TaxDiscount):
    def apply(self, price: int) -> int:
        return price

class TaxTenPercent(TaxDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class TaxPriceEngine:
    def __init__(self, discount: TaxDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "tax"
