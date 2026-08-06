"""DesignPatternsSolid | kind=solid | label=ocp | domain=inventory | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class InventoryNoDiscount(InventoryDiscount):
    def apply(self, price: int) -> int:
        return price

class InventoryTenPercent(InventoryDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class InventoryPriceEngine:
    def __init__(self, discount: InventoryDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "inventory"
