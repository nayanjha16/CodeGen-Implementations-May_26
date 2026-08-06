"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=sms | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class SmsPrototype:
    label: str
    weight: int

    def copy(self) -> "SmsPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
