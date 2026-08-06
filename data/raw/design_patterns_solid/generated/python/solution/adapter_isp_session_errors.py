"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=session | tier=errors"""
from __future__ import annotations

class SessionLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-session"

class SessionTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SessionAdapter(SessionTarget):
    def __init__(self, legacy: SessionLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
