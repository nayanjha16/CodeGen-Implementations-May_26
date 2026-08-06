"""DesignPatternsSolid | kind=solid | label=ocp | domain=plugin | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class PluginNoDiscount(PluginDiscount):
    def apply(self, price: int) -> int:
        return price

class PluginTenPercent(PluginDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class PluginPriceEngine:
    def __init__(self, discount: PluginDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "plugin"
