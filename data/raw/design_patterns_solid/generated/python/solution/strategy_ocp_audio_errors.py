"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=audio | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AudioStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class AudioNormalStrategy(AudioStrategy):
    def apply(self, amount: int) -> int:
        return amount

class AudioDiscountStrategy(AudioStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class AudioContext:
    def __init__(self, strategy: AudioStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: AudioStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount >= 0")
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "audio-strategy"
