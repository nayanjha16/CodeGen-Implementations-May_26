"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=booking | tier=logging"""
from __future__ import annotations

class BookingValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class BookingWriter:
    def write(self, v: str) -> str:
        return f"wrote-booking:{v}"

class BookingFacade:
    def __init__(self) -> None:
        self.validator = BookingValidator()
        self.writer = BookingWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
