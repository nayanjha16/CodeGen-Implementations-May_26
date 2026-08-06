"""DesignPatternsSolid | kind=solid | label=ocp | domain=feed | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class FeedDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class FeedNoDiscount(FeedDiscount):
    def apply(self, price: int) -> int:
        return price

class FeedTenPercent(FeedDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class FeedPriceEngine:
    def __init__(self, discount: FeedDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "feed"
