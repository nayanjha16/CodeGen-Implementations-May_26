"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=plugin | tier=logging"""
from __future__ import annotations

class PluginLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-plugin"

class PluginTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class PluginAdapter(PluginTarget):
    def __init__(self, legacy: PluginLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
