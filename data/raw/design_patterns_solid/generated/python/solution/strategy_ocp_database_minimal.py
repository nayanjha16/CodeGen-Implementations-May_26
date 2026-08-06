"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=database | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class DatabaseNormalStrategy(DatabaseStrategy):
    def apply(self, amount: int) -> int:
        return amount

class DatabaseDiscountStrategy(DatabaseStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class DatabaseContext:
    def __init__(self, strategy: DatabaseStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: DatabaseStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "database-strategy"
