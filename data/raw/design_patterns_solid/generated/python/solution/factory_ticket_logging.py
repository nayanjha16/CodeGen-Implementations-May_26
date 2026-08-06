"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=ticket | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TicketProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class TicketBasicProduct(TicketProduct):
    def operate(self) -> str:
        return "basic-ticket"

class TicketPremiumProduct(TicketProduct):
    def operate(self) -> str:
        return "premium-ticket"

class TicketFactory:
    def create(self, type_name: str) -> TicketProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return TicketPremiumProduct()
        return TicketBasicProduct()
