"""
codespec.model.expressions.literal

CSR v1.0 Literal Expression

Represents constant values embedded directly in source code.

Examples:
- integers
- floats
- strings
- booleans
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codespec.model.expressions.base import Expression
from codespec.core.enums import ExpressionKind


# ------------------------------------------------------------
# Literal Expression
# ------------------------------------------------------------

@dataclass
class Literal(Expression):
    """
    Immutable constant value.
    """

    value: Any
    literal_type: str = "UNKNOWN"

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = ExpressionKind.LITERAL.name
        self.pure = True

        # Infer simple literal type (lightweight, extendable later)
        self.literal_type = self._infer_type(self.value)

    # --------------------------------------------------------

    def _infer_type(self, value: Any) -> str:
        """
        Infer primitive CSR type from Python value.
        """
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, str):
            return "STRING"
        elif value is None:
            return "VOID"
        else:
            return "UNKNOWN"

    # --------------------------------------------------------

    def get_value(self) -> Any:
        return self.value