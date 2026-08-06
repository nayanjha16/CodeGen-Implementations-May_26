"""DesignPatternsSolid | kind=design_pattern | label=facade | domain=cart | tier=minimal"""
from __future__ import annotations

class CartValidator:
    def ok(self, v: str) -> bool:
        return bool(v)

class CartWriter:
    def write(self, v: str) -> str:
        return f"wrote-cart:{v}"

class CartFacade:
    def __init__(self) -> None:
        self.validator = CartValidator()
        self.writer = CartWriter()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
