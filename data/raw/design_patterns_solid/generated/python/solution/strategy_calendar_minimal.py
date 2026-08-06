"""DesignPatternsSolid | kind=design_pattern | label=strategy | domain=calendar | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarStrategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class CalendarNormalStrategy(CalendarStrategy):
    def apply(self, amount: int) -> int:
        return amount

class CalendarDiscountStrategy(CalendarStrategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class CalendarContext:
    def __init__(self, strategy: CalendarStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: CalendarStrategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "calendar-strategy"
