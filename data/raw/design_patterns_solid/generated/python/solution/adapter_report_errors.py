"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=report | tier=errors"""
from __future__ import annotations

class ReportLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-report"

class ReportTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class ReportAdapter(ReportTarget):
    def __init__(self, legacy: ReportLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
