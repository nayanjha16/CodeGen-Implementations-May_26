"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=shipping | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class ShippingPrototype:
    label: str
    weight: int

    def copy(self) -> "ShippingPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
