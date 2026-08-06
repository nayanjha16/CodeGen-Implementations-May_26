"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=calendar | tier=logging"""
from __future__ import annotations

class CalendarLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-calendar"

class CalendarTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class CalendarAdapter(CalendarTarget):
    def __init__(self, legacy: CalendarLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
