"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=session | tier=logging"""
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
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return SessionPremiumProduct()
        return SessionBasicProduct()
