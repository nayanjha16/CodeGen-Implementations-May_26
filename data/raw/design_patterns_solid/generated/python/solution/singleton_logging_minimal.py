"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=logging | tier=minimal"""
from __future__ import annotations

class LoggingSingleton:
    _instance: "LoggingSingleton | None" = None

    def __new__(cls) -> "LoggingSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value

    def get_value(self) -> str:
        return self.value
