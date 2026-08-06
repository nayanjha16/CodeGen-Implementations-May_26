"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=logging | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class LoggingPrototype:
    label: str
    weight: int

    def copy(self) -> "LoggingPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
