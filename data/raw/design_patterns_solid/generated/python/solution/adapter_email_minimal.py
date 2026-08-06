"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=email | tier=minimal"""
from __future__ import annotations

class EmailLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-email"

class EmailTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class EmailAdapter(EmailTarget):
    def __init__(self, legacy: EmailLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
