"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=game | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class GamePrototype:
    label: str
    weight: int

    def copy(self) -> "GamePrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
