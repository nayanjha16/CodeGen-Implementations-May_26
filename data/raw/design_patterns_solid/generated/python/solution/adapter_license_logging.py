"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=license | tier=logging"""
from __future__ import annotations

class LicenseLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-license"

class LicenseTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class LicenseAdapter(LicenseTarget):
    def __init__(self, legacy: LicenseLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
