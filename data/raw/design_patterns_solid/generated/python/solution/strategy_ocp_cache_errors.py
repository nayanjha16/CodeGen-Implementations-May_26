"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=cache | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class CacheNormalStrategy(CacheStrategy):
    def apply(self, amount: int) -> int:
        return amount

class CacheDiscountStrategy(CacheStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class CacheContext:
    def __init__(self, strategy: CacheStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: CacheStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "cache-strategy"
