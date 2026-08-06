"""DesignPatternsSolid | kind=solid | label=ocp | domain=ticket | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class TicketNoDiscount(TicketDiscount):
    def apply(self, price: int) -> int:
        return price

class TicketTenPercent(TicketDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class TicketPriceEngine:
    def __init__(self, discount: TicketDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "ticket"
