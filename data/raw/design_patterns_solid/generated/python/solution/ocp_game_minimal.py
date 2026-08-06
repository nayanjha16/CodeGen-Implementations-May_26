"""DesignPatternsSolid | kind=solid | label=ocp | domain=game | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class GameDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class GameNoDiscount(GameDiscount):
    def apply(self, price: int) -> int:
        return price

class GameTenPercent(GameDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class GamePriceEngine:
    def __init__(self, discount: GameDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "game"
