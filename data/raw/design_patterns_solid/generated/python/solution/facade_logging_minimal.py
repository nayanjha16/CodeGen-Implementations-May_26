"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=logging | tier=minimal"""
from __future__ import annotations

class LoggingValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class LoggingWriter:
    def write(self, v: str) -> str:
        return f"wrote-logging:{v}"

class LoggingFacade:
    def __init__(self) -> None:
        self.validator = LoggingValidator()
        self.writer = LoggingWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
