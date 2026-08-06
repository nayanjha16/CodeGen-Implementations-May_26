"""DesignPatternsSolid | kind=design_pattern | label=adapter | domain=comment | tier=logging"""
from __future__ import annotations

class CommentLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-comment"

class CommentTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class CommentAdapter(CommentTarget):
    def __init__(self, legacy: CommentLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
