"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=config | tier=minimal"""
from __future__ import annotations

class ConfigLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-config"

class ConfigTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class ConfigAdapter(ConfigTarget):
    def __init__(self, legacy: ConfigLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
