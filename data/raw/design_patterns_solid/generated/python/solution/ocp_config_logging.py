"""DesignPatternsSolid | kind=solid | label=ocp | domain=config | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class ConfigNoDiscount(ConfigDiscount):
    def apply(self, price: int) -> int:
        return price

class ConfigTenPercent(ConfigDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class ConfigPriceEngine:
    def __init__(self, discount: ConfigDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "config"
