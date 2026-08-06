"""DesignPatternsSolid | kind=solid | label=ocp | domain=logging | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class LoggingNoDiscount(LoggingDiscount):
    def apply(self, price: int) -> int:
        return price

class LoggingTenPercent(LoggingDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class LoggingPriceEngine:
    def __init__(self, discount: LoggingDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "logging"
