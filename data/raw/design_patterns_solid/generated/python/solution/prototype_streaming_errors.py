"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=streaming | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class StreamingPrototype:
    label: str
    weight: int

    def copy(self) -> "StreamingPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
