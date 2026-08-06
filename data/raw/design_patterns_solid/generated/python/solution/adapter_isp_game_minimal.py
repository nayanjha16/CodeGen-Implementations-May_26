"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=game | tier=minimal"""
from __future__ import annotations

class GameLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-game"

class GameTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class GameAdapter(GameTarget):
    def __init__(self, legacy: GameLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
