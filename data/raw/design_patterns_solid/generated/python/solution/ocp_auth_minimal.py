"""DesignPatternsSolid | kind=solid | label=ocp | domain=auth | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class AuthNoDiscount(AuthDiscount):
    def apply(self, price: int) -> int:
        return price

class AuthTenPercent(AuthDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class AuthPriceEngine:
    def __init__(self, discount: AuthDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "auth"
