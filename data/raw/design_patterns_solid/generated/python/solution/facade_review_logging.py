"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=review | tier=logging"""
from __future__ import annotations

class ReviewValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class ReviewWriter:
    def write(self, v: str) -> str:
        return f"wrote-review:{v}"

class ReviewFacade:
    def __init__(self) -> None:
        self.validator = ReviewValidator()
        self.writer = ReviewWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
