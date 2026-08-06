"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=backup | tier=errors"""
from __future__ import annotations

class BackupValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class BackupWriter:
    def write(self, v: str) -> str:
        return f"wrote-backup:{v}"

class BackupFacade:
    def __init__(self) -> None:
        self.validator = BackupValidator()
        self.writer = BackupWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
