"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=payments | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class PaymentsPrototype:
    label: str
    weight: int

    def copy(self) -> "PaymentsPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
