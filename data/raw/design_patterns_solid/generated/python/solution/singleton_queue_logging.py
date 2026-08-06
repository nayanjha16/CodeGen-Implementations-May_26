"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=queue | tier=logging"""
from __future__ import annotations

class QueueSingleton:
    _instance: "QueueSingleton | None" = None

    def __new__(cls) -> "QueueSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value
        print(f"[log] set {value}")

    def get_value(self) -> str:
        return self.value
