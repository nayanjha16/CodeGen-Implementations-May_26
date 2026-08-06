"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=inventory | tier=logging"""
from __future__ import annotations

class InventoryLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-inventory"

class InventoryTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class InventoryAdapter(InventoryTarget):
    def __init__(self, legacy: InventoryLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
