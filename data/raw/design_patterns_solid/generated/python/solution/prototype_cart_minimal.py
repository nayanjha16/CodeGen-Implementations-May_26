"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=cart | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class CartPrototype:
    label: str
    weight: int

    def copy(self) -> "CartPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
