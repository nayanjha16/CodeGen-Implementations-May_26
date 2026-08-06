"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=search | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class SearchProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class SearchBasicProduct(SearchProduct):
    def operate(self) -> str:
        return "basic-search"

class SearchPremiumProduct(SearchProduct):
    def operate(self) -> str:
        return "premium-search"

class SearchFactory:
    def create(self, type_name: str) -> SearchProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return SearchPremiumProduct()
        return SearchBasicProduct()
