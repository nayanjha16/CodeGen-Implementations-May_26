"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=discount | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DiscountProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class DiscountBasicProduct(DiscountProduct):
    def operate(self) -> str:
        return "basic-discount"

class DiscountPremiumProduct(DiscountProduct):
    def operate(self) -> str:
        return "premium-discount"

class DiscountFactory:
    def create(self, type_name: str) -> DiscountProduct:
        if type_name.lower() == "premium":
            return DiscountPremiumProduct()
        return DiscountBasicProduct()
