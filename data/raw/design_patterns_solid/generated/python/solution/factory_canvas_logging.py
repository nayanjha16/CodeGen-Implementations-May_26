"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=canvas | tier=logging"""
from __future__ import annotations

from abc import ABC, abstractmethod

class CanvasProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class CanvasBasicProduct(CanvasProduct):
    def operate(self) -> str:
        return "basic-canvas"

class CanvasPremiumProduct(CanvasProduct):
    def operate(self) -> str:
        return "premium-canvas"

class CanvasFactory:
    def create(self, type_name: str) -> CanvasProduct:
        print(f"[log] create {type_name}")
        if type_name.lower() == "premium":
            return CanvasPremiumProduct()
        return CanvasBasicProduct()
