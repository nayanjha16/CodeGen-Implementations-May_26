"""
codespec.model.expressions.binary_operation

CSR v1.0 BinaryOperation Expression

Represents all binary computations in a unified semantic form.

Examples:
- arithmetic: +, -, *, /
- comparison: >, <, ==
- logical: AND, OR
"""

from __future__ import annotations

from dataclasses import dataclass

from codespec.model.expressions.base import Expression
from codespec.core.enums import ExpressionKind


# ------------------------------------------------------------
# Binary Operation Expression
# ------------------------------------------------------------

@dataclass
class BinaryOperation(Expression):
    """
    Represents a binary operation between two expressions.
    """

    left: Expression
    right: Expression
    operator: str  # normalized operator (ADD, SUB, GT, AND, etc.)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = ExpressionKind.BINARY_OPERATION.name
        self.pure = True  # assumed pure unless later analysis says otherwise

        # Attach children in ownership tree
        self.add_child(self.left)
        self.add_child(self.right)

    # --------------------------------------------------------

    def get_operator(self) -> str:
        return self.operator