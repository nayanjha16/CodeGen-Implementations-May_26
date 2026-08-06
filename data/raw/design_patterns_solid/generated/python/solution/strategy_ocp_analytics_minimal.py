"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=analytics | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AnalyticsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class AnalyticsNormalStrategy(AnalyticsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class AnalyticsDiscountStrategy(AnalyticsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class AnalyticsContext:
    def __init__(self, strategy: AnalyticsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: AnalyticsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "analytics-strategy"
