"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=sensors | tier=minimal"""
from __future__ import annotations

class SensorsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-sensors"

class SensorsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SensorsAdapter(SensorsTarget):
    def __init__(self, legacy: SensorsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
