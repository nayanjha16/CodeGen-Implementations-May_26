"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=config | tier=logging"""
from __future__ import annotations

class ConfigValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class ConfigWriter:
    def write(self, v: str) -> str:
        return f"wrote-config:{v}"

class ConfigFacade:
    def __init__(self) -> None:
        self.validator = ConfigValidator()
        self.writer = ConfigWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
