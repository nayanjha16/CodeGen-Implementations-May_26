"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=http | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class HttpPrototype:
    label: str
    weight: int

    def copy(self) -> "HttpPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
