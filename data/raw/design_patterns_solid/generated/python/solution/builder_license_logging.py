"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=license | tier=logging"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class LicenseConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class LicenseConfigBuilder:
    def __init__(self) -> None:
        self._name = "license"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "LicenseConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "LicenseConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "LicenseConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> LicenseConfig:
        return LicenseConfig(self._name, self._limit, self._enabled)
