"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=email | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EmailProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class EmailBasicProduct(EmailProduct):
    def operate(self) -> str:
        return "basic-email"

class EmailPremiumProduct(EmailProduct):
    def operate(self) -> str:
        return "premium-email"

class EmailFactory:
    def create(self, type_name: str) -> EmailProduct:
        if type_name.lower() == "premium":
            return EmailPremiumProduct()
        return EmailBasicProduct()
