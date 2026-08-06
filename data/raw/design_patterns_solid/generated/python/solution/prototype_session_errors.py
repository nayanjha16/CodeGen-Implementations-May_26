"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=session | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class SessionPrototype:
    label: str
    weight: int

    def copy(self) -> "SessionPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
