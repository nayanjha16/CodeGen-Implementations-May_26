"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=payments | tier=errors"""
from __future__ import annotations

class PaymentsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class PaymentsWriter:
    def write(self, v: str) -> str:
        return f"wrote-payments:{v}"

class PaymentsFacade:
    def __init__(self) -> None:
        self.validator = PaymentsValidator()
        self.writer = PaymentsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
