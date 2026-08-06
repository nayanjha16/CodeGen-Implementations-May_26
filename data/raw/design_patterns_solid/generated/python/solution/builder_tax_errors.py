"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=tax | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class TaxConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class TaxConfigBuilder:
    def __init__(self) -> None:
        self._name = "tax"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "TaxConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "TaxConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "TaxConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> TaxConfig:
        return TaxConfig(self._name, self._limit, self._enabled)
