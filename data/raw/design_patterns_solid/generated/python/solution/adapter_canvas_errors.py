"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=canvas | tier=errors"""
from __future__ import annotations

class CanvasLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-canvas"

class CanvasTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class CanvasAdapter(CanvasTarget):
    def __init__(self, legacy: CanvasLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
