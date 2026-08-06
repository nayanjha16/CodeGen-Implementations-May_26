"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=cache | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CacheProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class CacheBasicProduct(CacheProduct):
    def operate(self) -> str:
        return "basic-cache"

class CachePremiumProduct(CacheProduct):
    def operate(self) -> str:
        return "premium-cache"

class CacheFactory:
    def create(self, type_name: str) -> CacheProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return CachePremiumProduct()
        return CacheBasicProduct()
