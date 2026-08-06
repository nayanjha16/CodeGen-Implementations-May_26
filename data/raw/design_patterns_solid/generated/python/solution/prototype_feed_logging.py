"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=feed | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class FeedPrototype:
    label: str
    weight: int

    def copy(self) -> "FeedPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
