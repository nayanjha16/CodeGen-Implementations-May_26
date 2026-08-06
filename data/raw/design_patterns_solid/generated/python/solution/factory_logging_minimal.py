"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=logging | tier=minimal"""
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
        if type_name.lower() == "premium":
            return LoggingPremiumProduct()
        return LoggingBasicProduct()
