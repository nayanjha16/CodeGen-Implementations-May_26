"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=chat | tier=errors"""
from __future__ import annotations

class ChatValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class ChatWriter:
    def write(self, v: str) -> str:
        return f"wrote-chat:{v}"

class ChatFacade:
    def __init__(self) -> None:
        self.validator = ChatValidator()
        self.writer = ChatWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
