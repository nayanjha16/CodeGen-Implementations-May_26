"""DesignPatternsSolid | kind=combo | label=adapter+isp | domain=todo | tier=logging"""
from __future__ import annotations

class TodoLegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-todo"

class TodoTarget:
    def fetch(self) -> str:
        raise NotImplementedError

class TodoAdapter(TodoTarget):
    def __init__(self, legacy: TodoLegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
