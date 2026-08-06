"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=http | tier=minimal"""
from __future__ import annotations

class HttpLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-http"

class HttpTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class HttpAdapter(HttpTarget):
    def __init__(self, legacy: HttpLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
