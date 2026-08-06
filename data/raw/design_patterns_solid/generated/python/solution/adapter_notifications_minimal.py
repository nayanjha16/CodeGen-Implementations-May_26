"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=notifications | tier=minimal"""
from __future__ import annotations

class NotificationsLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-notifications"

class NotificationsTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class NotificationsAdapter(NotificationsTarget):
    def __init__(self, legacy: NotificationsLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
