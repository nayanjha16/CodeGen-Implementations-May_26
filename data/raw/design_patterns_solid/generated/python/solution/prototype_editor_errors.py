"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=editor | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class EditorPrototype:
    label: str
    weight: int

    def copy(self) -> "EditorPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
