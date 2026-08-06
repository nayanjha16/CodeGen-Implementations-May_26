"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=search | tier=minimal"""
from __future__ import annotations

class SearchSingleton:
    _instance: "SearchSingleton | None" = None

    def __new__(cls) -> "SearchSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value

    def get_value(self) -> str:
        return self.value
