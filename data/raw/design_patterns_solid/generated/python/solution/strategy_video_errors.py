"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=video | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class VideoStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class VideoNormalStrategy(VideoStrategy):
    def apply(self, amount: int) -> int:
        return amount

class VideoDiscountStrategy(VideoStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class VideoContext:
    def __init__(self, strategy: VideoStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: VideoStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "video-strategy"
