"""DesignPatternsSolid | kind=solid | label=ocp | domain=queue | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class QueueNoDiscount(QueueDiscount):
    def apply(self, price: int) -> int:
        return price

class QueueTenPercent(QueueDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class QueuePriceEngine:
    def __init__(self, discount: QueueDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "queue"
