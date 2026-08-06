"""DesignPatternsSolid | kind=design_pattern | label=prototype | domain=notifications | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass
import copy

@dataclass
class NotificationsPrototype:
    label: str
    weight: int

    def copy(self) -> "NotificationsPrototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{self.label}#{self.weight}"
