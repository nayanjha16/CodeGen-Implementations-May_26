"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=cache | tier=logging"""
from __future__ import annotations

class CacheValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class CacheWriter:
    def write(self, v: str) -> str:
        return f"wrote-cache:{v}"

class CacheFacade:
    def __init__(self) -> None:
        self.validator = CacheValidator()
        self.writer = CacheWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
