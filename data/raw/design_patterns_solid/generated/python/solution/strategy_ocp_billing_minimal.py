"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class BillingNormalStrategy(BillingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class BillingDiscountStrategy(BillingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class BillingContext:
    def __init__(self, strategy: BillingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: BillingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "billing-strategy"
