"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=search | tier=minimal"""
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
        if type_name.lower() == "premium":
            return SearchPremiumProduct()
        return SearchBasicProduct()
