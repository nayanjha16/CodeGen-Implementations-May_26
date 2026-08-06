"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=metrics | tier=minimal"""
from __future__ import annotations

class MetricsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-metrics"

class MetricsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class MetricsAdapter(MetricsTarget):
    def __init__(self, legacy: MetricsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
