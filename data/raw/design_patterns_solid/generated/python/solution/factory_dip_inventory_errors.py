"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=inventory | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class InventoryProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class InventoryBasicProduct(InventoryProduct):
    def operate(self) -> str:
        return "basic-inventory"

class InventoryPremiumProduct(InventoryProduct):
    def operate(self) -> str:
        return "premium-inventory"

class InventoryFactory:
    def create(self, type_name: str) -> InventoryProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return InventoryPremiumProduct()
        return InventoryBasicProduct()
