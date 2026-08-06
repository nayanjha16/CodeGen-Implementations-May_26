"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=feed | tier=logging"""
from __future__ import annotations

class FeedValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class FeedWriter:
    def write(self, v: str) -> str:
        return f"wrote-feed:{v}"

class FeedFacade:
    def __init__(self) -> None:
        self.validator = FeedValidator()
        self.writer = FeedWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
