"""DesignPatternsSolid | kind=design_pattern | label=interpreter | domain=report | tier=logging"""
from __future__ import annotations

class ReportInterpreter:
    def eval(self, expr: str) -> int:
        if "+" in expr:
            a, b = expr.split("+", 1)
            return int(a.strip()) + int(b.strip())
        return int(expr.strip())

    def tag(self) -> str:
        return "report-interp"
