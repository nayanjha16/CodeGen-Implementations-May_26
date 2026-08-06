"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=logging | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class LoggingProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class LoggingBasicProduct(LoggingProduct):
    def operate(self) -> str:
        return "basic-logging"

class LoggingPremiumProduct(LoggingProduct):
    def operate(self) -> str:
        return "premium-logging"

class LoggingFactory:
    def create(self, type_name: str) -> LoggingProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return LoggingPremiumProduct()
        return LoggingBasicProduct()
