"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=editor | tier=logging"""
from __future__ import annotations

class EditorValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class EditorWriter:
    def write(self, v: str) -> str:
        return f"wrote-editor:{v}"

class EditorFacade:
    def __init__(self) -> None:
        self.validator = EditorValidator()
        self.writer = EditorWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
