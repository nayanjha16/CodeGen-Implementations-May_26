"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=session | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class SessionNormalStrategy(SessionStrategy):
    def apply(self, amount: int) -> int:
        return amount

class SessionDiscountStrategy(SessionStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class SessionContext:
    def __init__(self, strategy: SessionStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SessionStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "session-strategy"
