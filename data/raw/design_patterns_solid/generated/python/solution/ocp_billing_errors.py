"""DesignPatternsSolid | kind=solid | label=ocp | domain=billing | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class BillingNoDiscount(BillingDiscount):
    def apply(self, price: int) -> int:
        return price

class BillingTenPercent(BillingDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class BillingPriceEngine:
    def __init__(self, discount: BillingDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "billing"
