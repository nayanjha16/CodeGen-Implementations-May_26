"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=scheduling | tier=logging"""
from __future__ import annotations

class SchedulingValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class SchedulingWriter:
    def write(self, v: str) -> str:
        return f"wrote-scheduling:{v}"

class SchedulingFacade:
    def __init__(self) -> None:
        self.validator = SchedulingValidator()
        self.writer = SchedulingWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
