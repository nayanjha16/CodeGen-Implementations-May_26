"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=auth | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class AuthProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class AuthBasicProduct(AuthProduct):
    def operate(self) -> str:
        return "basic-auth"

class AuthPremiumProduct(AuthProduct):
    def operate(self) -> str:
        return "premium-auth"

class AuthFactory:
    def create(self, type_name: str) -> AuthProduct:
        if type_name.lower() == "premium":
            return AuthPremiumProduct()
        return AuthBasicProduct()
