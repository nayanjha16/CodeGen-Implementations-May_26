"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=session | tier=minimal"""
from __future__ import annotations

class SessionValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class SessionWriter:
    def write(self, v: str) -> str:
        return f"wrote-session:{v}"

class SessionFacade:
    def __init__(self) -> None:
        self.validator = SessionValidator()
        self.writer = SessionWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
