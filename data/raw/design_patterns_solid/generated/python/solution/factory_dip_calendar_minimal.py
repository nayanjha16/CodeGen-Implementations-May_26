"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=calendar | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CalendarProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class CalendarBasicProduct(CalendarProduct):
    def operate(self) -> str:
        return "basic-calendar"

class CalendarPremiumProduct(CalendarProduct):
    def operate(self) -> str:
        return "premium-calendar"

class CalendarFactory:
    def create(self, type_name: str) -> CalendarProduct:
        if type_name.lower() == "premium":
            return CalendarPremiumProduct()
        return CalendarBasicProduct()
