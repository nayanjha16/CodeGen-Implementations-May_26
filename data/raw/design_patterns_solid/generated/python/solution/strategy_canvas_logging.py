"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=canvas | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class CanvasNormalStrategy(CanvasStrategy):
    def apply(self, amount: int) -> int:
        return amount

class CanvasDiscountStrategy(CanvasStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class CanvasContext:
    def __init__(self, strategy: CanvasStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: CanvasStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "canvas-strategy"
