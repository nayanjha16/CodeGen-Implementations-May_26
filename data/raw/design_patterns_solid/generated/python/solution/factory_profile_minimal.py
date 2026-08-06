"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=profile | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ProfileProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ProfileBasicProduct(ProfileProduct):
    def operate(self) -> str:
        return "basic-profile"

class ProfilePremiumProduct(ProfileProduct):
    def operate(self) -> str:
        return "premium-profile"

class ProfileFactory:
    def create(self, type_name: str) -> ProfileProduct:
        if type_name.lower() == "premium":
            return ProfilePremiumProduct()
        return ProfileBasicProduct()
