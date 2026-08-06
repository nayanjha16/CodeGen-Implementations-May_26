"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=comment | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CommentStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class CommentNormalStrategy(CommentStrategy):
    def apply(self, amount: int) -> int:
        return amount

class CommentDiscountStrategy(CommentStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class CommentContext:
    def __init__(self, strategy: CommentStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: CommentStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "comment-strategy"
