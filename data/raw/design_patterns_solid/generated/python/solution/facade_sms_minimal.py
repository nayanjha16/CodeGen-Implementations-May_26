"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=sms | tier=minimal"""
from __future__ import annotations

class SmsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class SmsWriter:
    def write(self, v: str) -> str:
        return f"wrote-sms:{v}"

class SmsFacade:
    def __init__(self) -> None:
        self.validator = SmsValidator()
        self.writer = SmsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
