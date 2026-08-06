"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=notes | tier=errors"""
from __future__ import annotations

class NotesLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-notes"

class NotesTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class NotesAdapter(NotesTarget):
    def __init__(self, legacy: NotesLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
