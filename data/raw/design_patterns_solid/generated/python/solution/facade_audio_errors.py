"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=audio | tier=errors"""
from __future__ import annotations

class AudioValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class AudioWriter:
    def write(self, v: str) -> str:
        return f"wrote-audio:{v}"

class AudioFacade:
    def __init__(self) -> None:
        self.validator = AudioValidator()
        self.writer = AudioWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
