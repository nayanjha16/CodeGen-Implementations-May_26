"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=logging | tier=logging"""
from __future__ import annotations

class LoggingLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-logging"

class LoggingTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class LoggingAdapter(LoggingTarget):
    def __init__(self, legacy: LoggingLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
