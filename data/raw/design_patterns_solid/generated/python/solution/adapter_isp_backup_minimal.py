"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=backup | tier=minimal"""
from __future__ import annotations

class BackupLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-backup"

class BackupTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class BackupAdapter(BackupTarget):
    def __init__(self, legacy: BackupLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
