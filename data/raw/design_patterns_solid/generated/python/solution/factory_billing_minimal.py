"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=billing | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BillingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class BillingBasicProduct(BillingProduct):
    def operate(self) -> str:
        return "basic-billing"

class BillingPremiumProduct(BillingProduct):
    def operate(self) -> str:
        return "premium-billing"

class BillingFactory:
    def create(self, type_name: str) -> BillingProduct:
        if type_name.lower() == "premium":
            return BillingPremiumProduct()
        return BillingBasicProduct()
