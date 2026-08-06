"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=streaming | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class StreamingNormalStrategy(StreamingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class StreamingDiscountStrategy(StreamingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class StreamingContext:
    def __init__(self, strategy: StreamingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: StreamingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "streaming-strategy"
