"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=shipping | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ShippingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ShippingBasicProduct(ShippingProduct):
    def operate(self) -> str:
        return "basic-shipping"

class ShippingPremiumProduct(ShippingProduct):
    def operate(self) -> str:
        return "premium-shipping"

class ShippingFactory:
    def create(self, type_name: str) -> ShippingProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return ShippingPremiumProduct()
        return ShippingBasicProduct()
