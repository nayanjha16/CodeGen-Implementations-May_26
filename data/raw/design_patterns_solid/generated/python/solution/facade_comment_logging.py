"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=comment | tier=logging"""
from __future__ import annotations

class CommentValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class CommentWriter:
    def write(self, v: str) -> str:
        return f"wrote-comment:{v}"

class CommentFacade:
    def __init__(self) -> None:
        self.validator = CommentValidator()
        self.writer = CommentWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
