"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=calendar | tier=errors"""
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
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return CalendarPremiumProduct()
        return CalendarBasicProduct()
