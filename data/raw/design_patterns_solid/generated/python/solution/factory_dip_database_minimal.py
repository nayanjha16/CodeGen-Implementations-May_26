"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=database | tier=minimal"""
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
        if type_name.lower() == "premium":
            return DatabasePremiumProduct()
        return DatabaseBasicProduct()
