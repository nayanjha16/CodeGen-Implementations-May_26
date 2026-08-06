"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=plugin | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class PluginNormalStrategy(PluginStrategy):
    def apply(self, amount: int) -> int:
        return amount

class PluginDiscountStrategy(PluginStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class PluginContext:
    def __init__(self, strategy: PluginStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: PluginStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "plugin-strategy"
