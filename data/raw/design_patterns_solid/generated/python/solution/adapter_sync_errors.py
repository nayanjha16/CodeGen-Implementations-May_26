"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=sync | tier=errors"""
from __future__ import annotations

class SyncLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-sync"

class SyncTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SyncAdapter(SyncTarget):
    def __init__(self, legacy: SyncLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
