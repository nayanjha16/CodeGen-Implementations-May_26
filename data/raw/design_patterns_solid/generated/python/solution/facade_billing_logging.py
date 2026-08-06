"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=billing | tier=logging"""
from __future__ import annotations

class BillingValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class BillingWriter:
    def write(self, v: str) -> str:
        return f"wrote-billing:{v}"

class BillingFacade:
    def __init__(self) -> None:
        self.validator = BillingValidator()
        self.writer = BillingWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
