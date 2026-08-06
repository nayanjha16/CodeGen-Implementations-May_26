"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=email | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class EmailConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class EmailConfigBuilder:
    def __init__(self) -> None:
        self._name = "email"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "EmailConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "EmailConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "EmailConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> EmailConfig:
        return EmailConfig(self._name, self._limit, self._enabled)
