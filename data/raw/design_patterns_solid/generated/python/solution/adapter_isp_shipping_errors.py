"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=shipping | tier=errors"""
from __future__ import annotations

class ShippingLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-shipping"

class ShippingTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class ShippingAdapter(ShippingTarget):
    def __init__(self, legacy: ShippingLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
