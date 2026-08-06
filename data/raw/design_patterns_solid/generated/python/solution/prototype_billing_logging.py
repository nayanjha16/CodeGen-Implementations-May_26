"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=billing | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class BillingPrototype:
    label: str
    weight: int

    def copy(self) -> "BillingPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
