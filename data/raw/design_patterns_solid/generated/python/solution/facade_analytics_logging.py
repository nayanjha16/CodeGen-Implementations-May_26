"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=analytics | tier=logging"""
from __future__ import annotations

class AnalyticsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class AnalyticsWriter:
    def write(self, v: str) -> str:
        return f"wrote-analytics:{v}"

class AnalyticsFacade:
    def __init__(self) -> None:
        self.validator = AnalyticsValidator()
        self.writer = AnalyticsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
