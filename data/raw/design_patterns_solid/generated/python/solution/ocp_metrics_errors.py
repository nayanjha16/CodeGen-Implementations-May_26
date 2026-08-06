"""DesignPatternsSolid | kind=solid | label=ocp | domain=metrics | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class MetricsNoDiscount(MetricsDiscount):
    def apply(self, price: int) -> int:
        return price

class MetricsTenPercent(MetricsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class MetricsPriceEngine:
    def __init__(self, discount: MetricsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "metrics"
