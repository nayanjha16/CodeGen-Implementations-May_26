"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=canvas | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class CanvasPrototype:
    label: str
    weight: int

    def copy(self) -> "CanvasPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
