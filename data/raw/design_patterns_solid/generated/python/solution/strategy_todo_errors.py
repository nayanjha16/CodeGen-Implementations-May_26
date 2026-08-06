"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=todo | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TodoStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class TodoNormalStrategy(TodoStrategy):
    def apply(self, amount: int) -> int:
        return amount

class TodoDiscountStrategy(TodoStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class TodoContext:
    def __init__(self, strategy: TodoStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: TodoStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "todo-strategy"
