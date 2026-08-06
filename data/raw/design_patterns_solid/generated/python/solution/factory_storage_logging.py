"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=storage | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class StorageProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class StorageBasicProduct(StorageProduct):
    def operate(self) -> str:
        return "basic-storage"

class StoragePremiumProduct(StorageProduct):
    def operate(self) -> str:
        return "premium-storage"

class StorageFactory:
    def create(self, type_name: str) -> StorageProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return StoragePremiumProduct()
        return StorageBasicProduct()
