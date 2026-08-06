"""DesignPatternsSolid | kind=solid | label=ocp | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class EmailNoDiscount(EmailDiscount):
    def apply(self, price: int) -> int:
        return price

class EmailTenPercent(EmailDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class EmailPriceEngine:
    def __init__(self, discount: EmailDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "email"
