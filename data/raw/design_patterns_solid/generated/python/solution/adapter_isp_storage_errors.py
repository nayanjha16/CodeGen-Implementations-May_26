"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=storage | tier=errors"""
from __future__ import annotations

class StorageLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-storage"

class StorageTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class StorageAdapter(StorageTarget):
    def __init__(self, legacy: StorageLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
