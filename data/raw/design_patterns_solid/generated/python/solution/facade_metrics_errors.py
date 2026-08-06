"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=metrics | tier=errors"""
from __future__ import annotations

class MetricsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class MetricsWriter:
    def write(self, v: str) -> str:
        return f"wrote-metrics:{v}"

class MetricsFacade:
    def __init__(self) -> None:
        self.validator = MetricsValidator()
        self.writer = MetricsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
