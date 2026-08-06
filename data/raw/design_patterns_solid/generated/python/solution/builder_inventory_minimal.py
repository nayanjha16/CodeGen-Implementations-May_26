"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=inventory | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class InventoryConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class InventoryConfigBuilder:
    def __init__(self) -> None:
        self._name = "inventory"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "InventoryConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "InventoryConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "InventoryConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> InventoryConfig:
        return InventoryConfig(self._name, self._limit, self._enabled)
