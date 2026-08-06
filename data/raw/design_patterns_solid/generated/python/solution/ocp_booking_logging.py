"""DesignPatternsSolid | kind=solid | label=ocp | domain=booking | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class BookingNoDiscount(BookingDiscount):
    def apply(self, price: int) -> int:
        return price

class BookingTenPercent(BookingDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class BookingPriceEngine:
    def __init__(self, discount: BookingDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "booking"
