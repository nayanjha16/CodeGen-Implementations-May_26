"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=wallet | tier=minimal"""
from __future__ import annotations

class WalletValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class WalletWriter:
    def write(self, v: str) -> str:
        return f"wrote-wallet:{v}"

class WalletFacade:
    def __init__(self) -> None:
        self.validator = WalletValidator()
        self.writer = WalletWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
