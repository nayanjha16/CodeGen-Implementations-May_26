"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=game | tier=minimal"""
from __future__ import annotations

class GameValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class GameWriter:
    def write(self, v: str) -> str:
        return f"wrote-game:{v}"

class GameFacade:
    def __init__(self) -> None:
        self.validator = GameValidator()
        self.writer = GameWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
