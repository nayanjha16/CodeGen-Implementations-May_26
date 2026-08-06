"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=widgets | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class WidgetsProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class WidgetsBasicProduct(WidgetsProduct):
    def operate(self) -> str:
        return "basic-widgets"

class WidgetsPremiumProduct(WidgetsProduct):
    def operate(self) -> str:
        return "premium-widgets"

class WidgetsFactory:
    def create(self, type_name: str) -> WidgetsProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return WidgetsPremiumProduct()
        return WidgetsBasicProduct()
