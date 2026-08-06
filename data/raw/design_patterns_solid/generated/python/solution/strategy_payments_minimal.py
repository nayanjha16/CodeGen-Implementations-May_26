"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=payments | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class PaymentsNormalStrategy(PaymentsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class PaymentsDiscountStrategy(PaymentsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class PaymentsContext:
    def __init__(self, strategy: PaymentsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: PaymentsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "payments-strategy"
