"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=discount | tier=minimal"""
from __future__ import annotations

class DiscountLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-discount"

class DiscountTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class DiscountAdapter(DiscountTarget):
    def __init__(self, legacy: DiscountLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
