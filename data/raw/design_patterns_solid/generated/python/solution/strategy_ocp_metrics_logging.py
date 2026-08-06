"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=metrics | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MetricsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class MetricsNormalStrategy(MetricsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class MetricsDiscountStrategy(MetricsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class MetricsContext:
    def __init__(self, strategy: MetricsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: MetricsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "metrics-strategy"
