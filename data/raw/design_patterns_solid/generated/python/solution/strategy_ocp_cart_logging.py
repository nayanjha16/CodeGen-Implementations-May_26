"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=cart | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class CartNormalStrategy(CartStrategy):
    def apply(self, amount: int) -> int:
        return amount

class CartDiscountStrategy(CartStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class CartContext:
    def __init__(self, strategy: CartStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: CartStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "cart-strategy"
