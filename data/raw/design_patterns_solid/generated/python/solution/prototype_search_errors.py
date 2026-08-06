"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=search | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class SearchPrototype:
    label: str
    weight: int

    def copy(self) -> "SearchPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
