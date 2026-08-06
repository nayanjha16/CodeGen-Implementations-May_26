"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=analytics | tier=logging"""
from __future__ import annotations

class AnalyticsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-analytics"

class AnalyticsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class AnalyticsAdapter(AnalyticsTarget):
    def __init__(self, legacy: AnalyticsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
