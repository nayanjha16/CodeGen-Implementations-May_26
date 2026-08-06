"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=sync | tier=minimal"""
from __future__ import annotations

class SyncSingleton:
    _instance: "SyncSingleton | None" = None

    def __new__(cls) -> "SyncSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value

    def get_value(self) -> str:
        return self.value
