"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=backup | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class BackupProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class BackupBasicProduct(BackupProduct):
    def operate(self) -> str:
        return "basic-backup"

class BackupPremiumProduct(BackupProduct):
    def operate(self) -> str:
        return "premium-backup"

class BackupFactory:
    def create(self, type_name: str) -> BackupProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return BackupPremiumProduct()
        return BackupBasicProduct()
