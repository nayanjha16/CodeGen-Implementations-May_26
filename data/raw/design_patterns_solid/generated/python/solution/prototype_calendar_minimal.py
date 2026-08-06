"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=calendar | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class CalendarPrototype:
    label: str
    weight: int

    def copy(self) -> "CalendarPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
