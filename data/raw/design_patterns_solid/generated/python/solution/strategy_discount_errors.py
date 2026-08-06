"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=discount | tier=errors"""
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
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "discount-strategy"
