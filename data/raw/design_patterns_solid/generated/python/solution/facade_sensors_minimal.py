"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=sensors | tier=minimal"""
from __future__ import annotations

class SensorsValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class SensorsWriter:
    def write(self, v: str) -> str:
        return f"wrote-sensors:{v}"

class SensorsFacade:
    def __init__(self) -> None:
        self.validator = SensorsValidator()
        self.writer = SensorsWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
