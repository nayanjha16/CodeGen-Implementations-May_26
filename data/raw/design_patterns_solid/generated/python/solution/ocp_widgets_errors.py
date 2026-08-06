"""DesignPatternsSolid | kind=solid | label=ocp | domain=widgets | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class WidgetsNoDiscount(WidgetsDiscount):
    def apply(self, price: int) -> int:
        return price

class WidgetsTenPercent(WidgetsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class WidgetsPriceEngine:
    def __init__(self, discount: WidgetsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "widgets"
