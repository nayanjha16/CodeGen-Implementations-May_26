"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=queue | tier=logging"""
from __future__ import annotations

class QueueLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-queue"

class QueueTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class QueueAdapter(QueueTarget):
    def __init__(self, legacy: QueueLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
