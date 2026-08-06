"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=sync | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SyncProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SyncBasicProduct(SyncProduct):
    def operate(self) -> str:
        return "basic-sync"

class SyncPremiumProduct(SyncProduct):
    def operate(self) -> str:
        return "premium-sync"

class SyncFactory:
    def create(self, type_name: str) -> SyncProduct:
        if type_name.lower() == "premium":
            return SyncPremiumProduct()
        return SyncBasicProduct()
