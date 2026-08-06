"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=streaming | tier=errors"""
from __future__ import annotations

class StreamingValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class StreamingWriter:
    def write(self, v: str) -> str:
        return f"wrote-streaming:{v}"

class StreamingFacade:
    def __init__(self) -> None:
        self.validator = StreamingValidator()
        self.writer = StreamingWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
