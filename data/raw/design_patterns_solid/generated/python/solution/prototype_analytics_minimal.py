"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=analytics | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class AnalyticsPrototype:
    label: str
    weight: int

    def copy(self) -> "AnalyticsPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
