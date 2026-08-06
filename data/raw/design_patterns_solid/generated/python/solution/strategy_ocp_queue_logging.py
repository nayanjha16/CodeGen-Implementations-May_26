"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=queue | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class QueueNormalStrategy(QueueStrategy):
    def apply(self, amount: int) -> int:
        return amount

class QueueDiscountStrategy(QueueStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class QueueContext:
    def __init__(self, strategy: QueueStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: QueueStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "queue-strategy"
