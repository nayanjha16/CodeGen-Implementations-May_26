"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=discount | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class DiscountPrototype:
    label: str
    weight: int

    def copy(self) -> "DiscountPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
