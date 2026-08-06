"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=editor | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class EditorNormalStrategy(EditorStrategy):
    def apply(self, amount: int) -> int:
        return amount

class EditorDiscountStrategy(EditorStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class EditorContext:
    def __init__(self, strategy: EditorStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: EditorStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "editor-strategy"
