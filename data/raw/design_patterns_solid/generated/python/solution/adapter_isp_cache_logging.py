"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=cache | tier=logging"""
from __future__ import annotations

class CacheLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-cache"

class CacheTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class CacheAdapter(CacheTarget):
    def __init__(self, legacy: CacheLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
