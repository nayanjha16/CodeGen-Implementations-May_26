"""DesignPatternsSolid | kind=solid | label=ocp | domain=session | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class SessionNoDiscount(SessionDiscount):
    def apply(self, price: int) -> int:
        return price

class SessionTenPercent(SessionDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class SessionPriceEngine:
    def __init__(self, discount: SessionDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "session"
