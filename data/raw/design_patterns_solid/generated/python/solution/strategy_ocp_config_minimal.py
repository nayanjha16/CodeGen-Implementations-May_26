"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=config | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class ConfigNormalStrategy(ConfigStrategy):
    def apply(self, amount: int) -> int:
        return amount

class ConfigDiscountStrategy(ConfigStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class ConfigContext:
    def __init__(self, strategy: ConfigStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: ConfigStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "config-strategy"
