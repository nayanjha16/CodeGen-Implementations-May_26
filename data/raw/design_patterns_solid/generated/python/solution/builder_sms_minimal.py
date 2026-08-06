"""DesignPatternsSolid | kind=design_pattern | label=builder | domain=sms | tier=minimal"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SmsConfig:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{self.name}:{self.limit}:{self.enabled}"

class SmsConfigBuilder:
    def __init__(self) -> None:
        self._name = "sms"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "SmsConfigBuilder":
        self._name = name
        return self

    def limit(self, limit: int) -> "SmsConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "SmsConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> SmsConfig:
        return SmsConfig(self._name, self._limit, self._enabled)
