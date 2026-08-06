"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=chat | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class ChatPrototype:
    label: str
    weight: int

    def copy(self) -> "ChatPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
