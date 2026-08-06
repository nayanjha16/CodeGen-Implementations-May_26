"""DesignPatternsSolid | kind=solid | label=ocp | domain=payments | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PaymentsDiscount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class PaymentsNoDiscount(PaymentsDiscount):
    def apply(self, price: int) -> int:
        return price

class PaymentsTenPercent(PaymentsDiscount):
    def apply(self, price: int) -> int:
        return price - price // 10

class PaymentsPriceEngine:
    def __init__(self, discount: PaymentsDiscount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "payments"
