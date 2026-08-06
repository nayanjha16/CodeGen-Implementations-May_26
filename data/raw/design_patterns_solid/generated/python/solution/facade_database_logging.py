"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=database | tier=logging"""
from __future__ import annotations

class DatabaseValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class DatabaseWriter:
    def write(self, v: str) -> str:
        return f"wrote-database:{v}"

class DatabaseFacade:
    def __init__(self) -> None:
        self.validator = DatabaseValidator()
        self.writer = DatabaseWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
