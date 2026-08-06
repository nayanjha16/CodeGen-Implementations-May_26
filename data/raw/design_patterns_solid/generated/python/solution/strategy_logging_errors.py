"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=logging | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class LoggingNormalStrategy(LoggingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class LoggingDiscountStrategy(LoggingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class LoggingContext:
    def __init__(self, strategy: LoggingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: LoggingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "logging-strategy"
