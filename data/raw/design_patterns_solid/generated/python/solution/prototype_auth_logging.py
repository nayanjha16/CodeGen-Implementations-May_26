"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=auth | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class AuthPrototype:
    label: str
    weight: int

    def copy(self) -> "AuthPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
