"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=wallet | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class WalletConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class WalletConfigBuilder:
    def __init__(self) -> None:
        self._name = "wallet"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "WalletConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "WalletConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "WalletConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> WalletConfig:
        return WalletConfig(self._name, self._limit, self._enabled)
