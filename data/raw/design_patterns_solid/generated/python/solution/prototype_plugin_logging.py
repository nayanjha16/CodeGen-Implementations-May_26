"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=plugin | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class PluginPrototype:
    label: str
    weight: int

    def copy(self) -> "PluginPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
