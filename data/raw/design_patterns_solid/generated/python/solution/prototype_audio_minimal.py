"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=audio | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class AudioPrototype:
    label: str
    weight: int

    def copy(self) -> "AudioPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
