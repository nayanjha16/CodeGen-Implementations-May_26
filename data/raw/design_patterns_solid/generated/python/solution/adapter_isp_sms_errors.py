"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=sms | tier=errors"""
from __future__ import annotations

class SmsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-sms"

class SmsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class SmsAdapter(SmsTarget):
    def __init__(self, legacy: SmsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
