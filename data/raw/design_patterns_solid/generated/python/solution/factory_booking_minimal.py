"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=booking | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BookingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class BookingBasicProduct(BookingProduct):
    def operate(self) -> str:
        return "basic-booking"

class BookingPremiumProduct(BookingProduct):
    def operate(self) -> str:
        return "premium-booking"

class BookingFactory:
    def create(self, type_name: str) -> BookingProduct:
        if type_name.lower() == "premium":
            return BookingPremiumProduct()
        return BookingBasicProduct()
