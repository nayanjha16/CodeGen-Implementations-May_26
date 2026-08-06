"""DesignPatternsSolid | kind=design_pattern | label=factory | domain=editor | tier=minimal"""
from __future__ import annotations

from abc import ABC, abstractmethod

class EditorProduct(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class EditorBasicProduct(EditorProduct):
    def operate(self) -> str:
        return "basic-editor"

class EditorPremiumProduct(EditorProduct):
    def operate(self) -> str:
        return "premium-editor"

class EditorFactory:
    def create(self, type_name: str) -> EditorProduct:
        if type_name.lower() == "premium":
            return EditorPremiumProduct()
        return EditorBasicProduct()
