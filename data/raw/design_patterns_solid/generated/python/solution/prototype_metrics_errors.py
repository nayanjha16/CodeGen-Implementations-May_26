"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=metrics | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class MetricsPrototype:
    label: str
    weight: int

    def copy(self) -> "MetricsPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
