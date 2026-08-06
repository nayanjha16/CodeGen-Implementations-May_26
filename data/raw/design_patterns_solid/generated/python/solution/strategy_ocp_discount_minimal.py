"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=discount | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class DiscountNormalStrategy(DiscountStrategy):
    def apply(self, amount: int) -> int:
        return amount

class DiscountDiscountStrategy(DiscountStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class DiscountContext:
    def __init__(self, strategy: DiscountStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: DiscountStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "discount-strategy"
