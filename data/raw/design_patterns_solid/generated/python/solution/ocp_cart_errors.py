"""DesignPatternsSolid | kind=solid | label=ocp | domain=cart | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CartDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class CartNoDiscount(CartDiscount):
    def apply(self, price: int) -> int:
        return price

class CartTenPercent(CartDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class CartPriceEngine:
    def __init__(self, discount: CartDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "cart"
