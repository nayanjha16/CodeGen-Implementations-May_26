"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=tax | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class TaxNormalStrategy(TaxStrategy):
    def apply(self, amount: int) -> int:
        return amount

class TaxDiscountStrategy(TaxStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class TaxContext:
    def __init__(self, strategy: TaxStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: TaxStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "tax-strategy"
