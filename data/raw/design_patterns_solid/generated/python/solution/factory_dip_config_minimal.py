"""DesignPatternsSolid | kind=combo | label=factory+dip | domain=config | tier=minimal"""
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
        if type_name.lower() == "premium":
            return ConfigPremiumProduct()
        return ConfigBasicProduct()
