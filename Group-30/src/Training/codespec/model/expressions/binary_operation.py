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

from codespec.model.expressions.base import Expression
from codespec.core.enums import ExpressionKind


class BinaryOperation(Expression):
    """
    Represents a binary operation like a + b.
    """

    def __init__(self, left, right, operator: str):
        super().__init__()

        self.left = left
        self.right = right
        self.operator = operator

        self.kind = ExpressionKind.BINARY_OPERATION.name
        self.pure = True

        # attach children for CSR graph traversal
        self.add_child(left)
        self.add_child(right)
