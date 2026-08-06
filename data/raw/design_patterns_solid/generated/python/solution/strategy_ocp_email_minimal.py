"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class EmailNormalStrategy(EmailStrategy):
    def apply(self, amount: int) -> int:
        return amount

class EmailDiscountStrategy(EmailStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class EmailContext:
    def __init__(self, strategy: EmailStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: EmailStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "email-strategy"
