"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=inventory | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class InventoryNormalStrategy(InventoryStrategy):
    def apply(self, amount: int) -> int:
        return amount

class InventoryDiscountStrategy(InventoryStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class InventoryContext:
    def __init__(self, strategy: InventoryStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: InventoryStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "inventory-strategy"
