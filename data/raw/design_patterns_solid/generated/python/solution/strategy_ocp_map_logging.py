"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=map | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class MapStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class MapNormalStrategy(MapStrategy):
    def apply(self, amount: int) -> int:
        return amount

class MapDiscountStrategy(MapStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class MapContext:
    def __init__(self, strategy: MapStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: MapStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "map-strategy"
