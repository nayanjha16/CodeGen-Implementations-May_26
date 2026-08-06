"""DesignPatternsSolid | kind=solid | label=ocp | domain=sync | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class SyncNoDiscount(SyncDiscount):
    def apply(self, price: int) -> int:
        return price

class SyncTenPercent(SyncDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class SyncPriceEngine:
    def __init__(self, discount: SyncDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "sync"
