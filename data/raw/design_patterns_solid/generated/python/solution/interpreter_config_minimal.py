"""DesignPatternsSolid | kind=design_pattern | label=interpreter | domain=config | tier=minimal"""
from __future__ import annotations

class ConfigInterpreter:
    def eval(self, expr: str) -> int:
        if "+" in expr:
            a, b = expr.split("+", 1)
            return int(a.strip()) + int(b.strip())
        return int(expr.strip())

    def tag(self) -> str:
        return "config-interp"
