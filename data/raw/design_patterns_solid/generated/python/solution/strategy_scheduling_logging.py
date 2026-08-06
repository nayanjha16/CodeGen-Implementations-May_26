"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=scheduling | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SchedulingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class SchedulingNormalStrategy(SchedulingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class SchedulingDiscountStrategy(SchedulingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class SchedulingContext:
    def __init__(self, strategy: SchedulingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SchedulingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "scheduling-strategy"
