"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=wallet | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class WalletPrototype:
    label: str
    weight: int

    def copy(self) -> "WalletPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
