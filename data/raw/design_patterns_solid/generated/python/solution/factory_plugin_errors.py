"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=plugin | tier=errors"""
from __future__ import annotations

from abc import ABC, abstractmethod

class PluginProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class PluginBasicProduct(PluginProduct):
    def operate(self) -> str:
        return "basic-plugin"

class PluginPremiumProduct(PluginProduct):
    def operate(self) -> str:
        return "premium-plugin"

class PluginFactory:
    def create(self, type_name: str) -> PluginProduct:
        if not type_name:
            raise ValueError("type required")
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return PluginPremiumProduct()
        return PluginBasicProduct()
