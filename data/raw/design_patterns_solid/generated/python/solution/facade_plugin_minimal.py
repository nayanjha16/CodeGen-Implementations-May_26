"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=plugin | tier=minimal"""
from __future__ import annotations

class PluginValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class PluginWriter:
    def write(self, v: str) -> str:
        return f"wrote-plugin:{v}"

class PluginFacade:
    def __init__(self) -> None:
        self.validator = PluginValidator()
        self.writer = PluginWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
