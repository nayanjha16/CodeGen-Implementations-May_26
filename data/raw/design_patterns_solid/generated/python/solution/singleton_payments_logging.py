"""DesignPatternsSolid | kind=design_pattern | label=singleton | domain=payments | tier=logging"""
from __future__ import annotations

class PaymentsSingleton:
    _instance: "PaymentsSingleton | None" = None

    def __new__(cls) -> "PaymentsSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
        self.value = value
        print(f"[log] set {value}")

    def get_value(self) -> str:
        return self.value
