"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=todo | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class TodoPrototype:
    label: str
    weight: int

    def copy(self) -> "TodoPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
