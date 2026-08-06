"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=storage | tier=errors"""
from __future__ import annotations

class StorageSingleton:
    _instance: "StorageSingleton | None" = None

    def __new__(cls) -> "StorageSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        if not value:
            raise ValueError("value required")
        self.value = value
        print(f"[log] set {value}")

    def get_value(self) -> str:
        return self.value
