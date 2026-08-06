"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=audio | tier=errors"""
from __future__ import annotations

class AudioLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-audio"

class AudioTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class AudioAdapter(AudioTarget):
    def __init__(self, legacy: AudioLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
