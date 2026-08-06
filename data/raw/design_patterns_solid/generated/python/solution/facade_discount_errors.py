"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=discount | tier=errors"""
from __future__ import annotations

class DiscountValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class DiscountWriter:
    def write(self, v: str) -> str:
        return f"wrote-discount:{v}"

class DiscountFacade:
    def __init__(self) -> None:
        self.validator = DiscountValidator()
        self.writer = DiscountWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
