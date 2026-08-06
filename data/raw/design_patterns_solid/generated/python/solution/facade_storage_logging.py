"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=storage | tier=logging"""
from __future__ import annotations

class StorageValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class StorageWriter:
    def write(self, v: str) -> str:
        return f"wrote-storage:{v}"

class StorageFacade:
    def __init__(self) -> None:
        self.validator = StorageValidator()
        self.writer = StorageWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
