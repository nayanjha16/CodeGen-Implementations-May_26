"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=report | tier=logging"""
from __future__ import annotations

class ReportValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class ReportWriter:
    def write(self, v: str) -> str:
        return f"wrote-report:{v}"

class ReportFacade:
    def __init__(self) -> None:
        self.validator = ReportValidator()
        self.writer = ReportWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
