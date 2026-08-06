"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=search | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class SearchNormalStrategy(SearchStrategy):
    def apply(self, amount: int) -> int:
        return amount

class SearchDiscountStrategy(SearchStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class SearchContext:
    def __init__(self, strategy: SearchStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SearchStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "search-strategy"
