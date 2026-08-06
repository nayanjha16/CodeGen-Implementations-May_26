"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=notes | tier=minimal"""
from __future__ import annotations

class NotesValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class NotesWriter:
    def write(self, v: str) -> str:
        return f"wrote-notes:{v}"

class NotesFacade:
    def __init__(self) -> None:
        self.validator = NotesValidator()
        self.writer = NotesWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
