"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=map | tier=errors"""
from __future__ import annotations

class MapValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class MapWriter:
    def write(self, v: str) -> str:
        return f"wrote-map:{v}"

class MapFacade:
    def __init__(self) -> None:
        self.validator = MapValidator()
        self.writer = MapWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
