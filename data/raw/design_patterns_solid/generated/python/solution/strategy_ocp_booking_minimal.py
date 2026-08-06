"""DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=booking | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class BookingNormalStrategy(BookingStrategy):
    def apply(self, amount: int) -> int:
        return amount

class BookingDiscountStrategy(BookingStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class BookingContext:
    def __init__(self, strategy: BookingStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: BookingStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "booking-strategy"
