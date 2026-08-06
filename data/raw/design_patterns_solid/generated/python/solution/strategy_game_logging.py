"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=game | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class GameNormalStrategy(GameStrategy):
    def apply(self, amount: int) -> int:
        return amount

class GameDiscountStrategy(GameStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class GameContext:
    def __init__(self, strategy: GameStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: GameStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "game-strategy"
