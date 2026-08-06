"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=email | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class EmailPrototype:
    label: str
    weight: int

    def copy(self) -> "EmailPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
