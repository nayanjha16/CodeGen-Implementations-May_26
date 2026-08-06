"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=database | tier=minimal"""
from __future__ import annotations

class DatabaseLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-database"

class DatabaseTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class DatabaseAdapter(DatabaseTarget):
    def __init__(self, legacy: DatabaseLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
