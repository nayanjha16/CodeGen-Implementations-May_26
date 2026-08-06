"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=http | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class HttpStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class HttpNormalStrategy(HttpStrategy):
    def apply(self, amount: int) -> int:
        return amount

class HttpDiscountStrategy(HttpStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class HttpContext:
    def __init__(self, strategy: HttpStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: HttpStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "http-strategy"
