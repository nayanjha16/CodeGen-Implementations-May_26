"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=chat | tier=minimal"""
from __future__ import annotations

class ChatLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-chat"

class ChatTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class ChatAdapter(ChatTarget):
    def __init__(self, legacy: ChatLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
