"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=map | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class MapPrototype:
    label: str
    weight: int

    def copy(self) -> "MapPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
