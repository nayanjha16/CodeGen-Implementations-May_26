"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=feed | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class FeedNormalStrategy(FeedStrategy):
    def apply(self, amount: int) -> int:
        return amount

class FeedDiscountStrategy(FeedStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class FeedContext:
    def __init__(self, strategy: FeedStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: FeedStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "feed-strategy"
