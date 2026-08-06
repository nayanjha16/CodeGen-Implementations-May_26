"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=widgets | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class WidgetsNormalStrategy(WidgetsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class WidgetsDiscountStrategy(WidgetsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class WidgetsContext:
    def __init__(self, strategy: WidgetsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: WidgetsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "widgets-strategy"
