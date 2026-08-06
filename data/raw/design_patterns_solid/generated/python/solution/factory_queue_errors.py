"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=queue | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class QueueProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class QueueBasicProduct(QueueProduct):
    def operate(self) -> str:
        return "basic-queue"

class QueuePremiumProduct(QueueProduct):
    def operate(self) -> str:
        return "premium-queue"

class QueueFactory:
    def create(self, type_name: str) -> QueueProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return QueuePremiumProduct()
        return QueueBasicProduct()
