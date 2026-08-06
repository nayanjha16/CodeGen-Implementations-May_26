"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=config | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ConfigProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class ConfigBasicProduct(ConfigProduct):
    def operate(self) -> str:
        return "basic-config"

class ConfigPremiumProduct(ConfigProduct):
    def operate(self) -> str:
        return "premium-config"

class ConfigFactory:
    def create(self, type_name: str) -> ConfigProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return ConfigPremiumProduct()
        return ConfigBasicProduct()
