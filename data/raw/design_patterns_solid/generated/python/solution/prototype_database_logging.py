"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=database | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class DatabasePrototype:
    label: str
    weight: int

    def copy(self) -> "DatabasePrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
