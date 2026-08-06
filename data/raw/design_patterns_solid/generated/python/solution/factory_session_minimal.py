"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=session | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SessionProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SessionBasicProduct(SessionProduct):
    def operate(self) -> str:
        return "basic-session"

class SessionPremiumProduct(SessionProduct):
    def operate(self) -> str:
        return "premium-session"

class SessionFactory:
    def create(self, type_name: str) -> SessionProduct:
        if type_name.lower() == "premium":
            return SessionPremiumProduct()
        return SessionBasicProduct()
