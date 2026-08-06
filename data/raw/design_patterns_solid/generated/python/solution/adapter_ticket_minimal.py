"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=ticket | tier=minimal"""
from __future__ import annotations

class TicketLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-ticket"

class TicketTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class TicketAdapter(TicketTarget):
    def __init__(self, legacy: TicketLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
