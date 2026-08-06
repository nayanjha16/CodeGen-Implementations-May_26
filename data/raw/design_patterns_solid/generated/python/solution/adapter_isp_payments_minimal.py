"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=payments | tier=minimal"""
from __future__ import annotations

class PaymentsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-payments"

class PaymentsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class PaymentsAdapter(PaymentsTarget):
    def __init__(self, legacy: PaymentsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
