"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=tax | tier=logging"""
from __future__ import annotations

class TaxValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class TaxWriter:
    def write(self, v: str) -> str:
        return f"wrote-tax:{v}"

class TaxFacade:
    def __init__(self) -> None:
        self.validator = TaxValidator()
        self.writer = TaxWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
