"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=payments | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PaymentsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class PaymentsConfigBuilder:
    def __init__(self) -> None:
        self._name = "payments"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "PaymentsConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "PaymentsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "PaymentsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> PaymentsConfig:
        return PaymentsConfig(self._name, self._limit, self._enabled)
