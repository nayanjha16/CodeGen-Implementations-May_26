"""DesignPatternsSolid | kind=solid | label=ocp | domain=cache | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class CacheNoDiscount(CacheDiscount):
    def apply(self, price: int) -> int:
        return price

class CacheTenPercent(CacheDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class CachePriceEngine:
    def __init__(self, discount: CacheDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "cache"
