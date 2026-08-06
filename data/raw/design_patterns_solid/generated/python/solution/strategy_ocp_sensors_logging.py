"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=sensors | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SensorsStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class SensorsNormalStrategy(SensorsStrategy):
    def apply(self, amount: int) -> int:
        return amount

class SensorsDiscountStrategy(SensorsStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class SensorsContext:
    def __init__(self, strategy: SensorsStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SensorsStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "sensors-strategy"
