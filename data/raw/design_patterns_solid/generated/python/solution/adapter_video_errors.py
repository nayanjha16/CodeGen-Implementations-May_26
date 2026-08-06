"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=video | tier=errors"""
from __future__ import annotations

class VideoLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-video"

class VideoTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class VideoAdapter(VideoTarget):
    def __init__(self, legacy: VideoLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
