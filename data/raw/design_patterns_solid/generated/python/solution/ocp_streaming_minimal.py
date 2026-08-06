"""DesignPatternsSolid | kind=solid | label=ocp | domain=streaming | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StreamingDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class StreamingNoDiscount(StreamingDiscount):
    def apply(self, price: int) -> int:
        return price

class StreamingTenPercent(StreamingDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class StreamingPriceEngine:
    def __init__(self, discount: StreamingDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "streaming"
