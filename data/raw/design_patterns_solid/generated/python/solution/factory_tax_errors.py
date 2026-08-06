"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=tax | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class TaxProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class TaxBasicProduct(TaxProduct):
    def operate(self) -> str:
        return "basic-tax"

class TaxPremiumProduct(TaxProduct):
    def operate(self) -> str:
        return "premium-tax"

class TaxFactory:
    def create(self, type_name: str) -> TaxProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return TaxPremiumProduct()
        return TaxBasicProduct()
