"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=search | tier=minimal"""
from __future__ import annotations

class SearchLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-search"

class SearchTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SearchAdapter(SearchTarget):
    def __init__(self, legacy: SearchLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
