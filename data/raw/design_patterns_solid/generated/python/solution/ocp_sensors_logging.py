"""DesignPatternsSolid | kind=solid | label=ocp | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class SensorsNoDiscount(SensorsDiscount):
    def apply(self, price: int) -> int:
        return price

class SensorsTenPercent(SensorsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class SensorsPriceEngine:
    def __init__(self, discount: SensorsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "sensors"
