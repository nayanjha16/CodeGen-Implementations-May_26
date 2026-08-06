"""DesignPatternsSolid | kind=design_pattern | label=interpreter | domain=metrics | tier=errors"""
from __future__ import annotations

class MetricsInterpreter:
    def eval(self, expr: str) -> int:
        if "+" in expr:
            a, b = expr.split("+", 1)
            return int(a.strip()) + int(b.strip())
        return int(expr.strip())

    def tag(self) -> str:
        return "metrics-interp"
