"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=cart | tier=logging"""
from __future__ import annotations

class CartLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-cart"

class CartTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class CartAdapter(CartTarget):
    def __init__(self, legacy: CartLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
