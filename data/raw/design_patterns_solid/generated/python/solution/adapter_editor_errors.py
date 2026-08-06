"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=editor | tier=errors"""
from __future__ import annotations

class EditorLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-editor"

class EditorTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class EditorAdapter(EditorTarget):
    def __init__(self, legacy: EditorLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
