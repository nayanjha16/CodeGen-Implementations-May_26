"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=notes | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class NotesStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class NotesNormalStrategy(NotesStrategy):
    def apply(self, amount: int) -> int:
        return amount

class NotesDiscountStrategy(NotesStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class NotesContext:
    def __init__(self, strategy: NotesStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: NotesStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "notes-strategy"
