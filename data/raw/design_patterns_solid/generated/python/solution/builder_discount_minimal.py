"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=discount | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class DiscountConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class DiscountConfigBuilder:
    def __init__(self) -> None:
        self._name = "discount"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "DiscountConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "DiscountConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "DiscountConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> DiscountConfig:
        return DiscountConfig(self._name, self._limit, self._enabled)
