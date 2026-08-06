"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=license | tier=logging"""
from __future__ import annotations

class LicenseValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class LicenseWriter:
    def write(self, v: str) -> str:
        return f"wrote-license:{v}"

class LicenseFacade:
    def __init__(self) -> None:
        self.validator = LicenseValidator()
        self.writer = LicenseWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
