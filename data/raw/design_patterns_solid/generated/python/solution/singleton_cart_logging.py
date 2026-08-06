"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=cart | tier=logging"""
from __future__ import annotations

class CartSingleton:
    _instance: "CartSingleton | None" = None

    def __new__(cls) -> "CartSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value
        print(f"[log] set {value}")

    def get_value(self) -> str:
        return self.value
