"""DesignPatternsSolid | kind=solid | label=ocp | domain=database | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class DatabaseNoDiscount(DatabaseDiscount):
    def apply(self, price: int) -> int:
        return price

class DatabaseTenPercent(DatabaseDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class DatabasePriceEngine:
    def __init__(self, discount: DatabaseDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "database"
