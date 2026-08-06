"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=billing | tier=errors"""
from __future__ import annotations

class BillingLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-billing"

class BillingTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class BillingAdapter(BillingTarget):
    def __init__(self, legacy: BillingLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
