"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=auth | tier=logging"""
from __future__ import annotations

class AuthLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-auth"

class AuthTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class AuthAdapter(AuthTarget):
    def __init__(self, legacy: AuthLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
