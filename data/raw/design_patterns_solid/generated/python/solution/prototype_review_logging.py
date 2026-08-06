"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=review | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class ReviewPrototype:
    label: str
    weight: int

    def copy(self) -> "ReviewPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
