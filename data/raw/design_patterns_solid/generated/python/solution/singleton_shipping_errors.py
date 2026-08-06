"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=shipping | tier=errors"""
from __future__ import annotations

class ShippingSingleton:
    _instance: "ShippingSingleton | None" = None

    def __new__(cls) -> "ShippingSingleton":
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
