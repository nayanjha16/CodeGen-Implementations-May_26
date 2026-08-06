"""DesignPatternsSolid | kind=solid | label=ocp | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class AnalyticsNoDiscount(AnalyticsDiscount):
    def apply(self, price: int) -> int:
        return price

class AnalyticsTenPercent(AnalyticsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class AnalyticsPriceEngine:
    def __init__(self, discount: AnalyticsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "analytics"
