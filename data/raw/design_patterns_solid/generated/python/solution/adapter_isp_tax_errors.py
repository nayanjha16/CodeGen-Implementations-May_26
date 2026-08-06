"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=tax | tier=errors"""
from __future__ import annotations

class TaxLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-tax"

class TaxTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class TaxAdapter(TaxTarget):
    def __init__(self, legacy: TaxLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
