"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=comment | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class CommentPrototype:
    label: str
    weight: int

    def copy(self) -> "CommentPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
