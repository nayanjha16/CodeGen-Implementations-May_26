"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=scheduling | tier=errors"""
from __future__ import annotations

class SchedulingLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-scheduling"

class SchedulingTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SchedulingAdapter(SchedulingTarget):
    def __init__(self, legacy: SchedulingLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
