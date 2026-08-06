"""DesignPatternsSolid | kind=solid | label=ocp | domain=discount | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class DiscountNoDiscount(DiscountDiscount):
    def apply(self, price: int) -> int:
        return price

class DiscountTenPercent(DiscountDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class DiscountPriceEngine:
    def __init__(self, discount: DiscountDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "discount"
