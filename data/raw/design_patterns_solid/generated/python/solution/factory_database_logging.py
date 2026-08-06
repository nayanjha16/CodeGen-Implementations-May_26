"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=database | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class DatabaseProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class DatabaseBasicProduct(DatabaseProduct):
    def operate(self) -> str:
        return "basic-database"

class DatabasePremiumProduct(DatabaseProduct):
    def operate(self) -> str:
        return "premium-database"

class DatabaseFactory:
    def create(self, type_name: str) -> DatabaseProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return DatabasePremiumProduct()
        return DatabaseBasicProduct()
