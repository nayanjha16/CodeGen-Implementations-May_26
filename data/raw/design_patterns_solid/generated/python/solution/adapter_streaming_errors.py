"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=streaming | tier=errors"""
from __future__ import annotations

class StreamingLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-streaming"

class StreamingTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class StreamingAdapter(StreamingTarget):
    def __init__(self, legacy: StreamingLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
