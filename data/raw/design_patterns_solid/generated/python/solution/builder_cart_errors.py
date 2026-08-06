"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=cart | tier=errors"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CartConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class CartConfigBuilder:
    def __init__(self) -> None:
        self._name = "cart"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "CartConfigBuilder":
        if not name:
            raise ValueError("name required")
        self._name = name
        return self

    def limit(self, limit: int) -> "CartConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "CartConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> CartConfig:
        return CartConfig(self._name, self._limit, self._enabled)
