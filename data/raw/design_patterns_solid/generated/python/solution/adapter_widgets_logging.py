"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=widgets | tier=logging"""
from __future__ import annotations

class WidgetsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-widgets"

class WidgetsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class WidgetsAdapter(WidgetsTarget):
    def __init__(self, legacy: WidgetsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
