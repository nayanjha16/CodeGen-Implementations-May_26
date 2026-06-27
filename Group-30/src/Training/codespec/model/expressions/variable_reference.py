"""
codespec.model.expressions.variable_reference

Safe CSR VariableReference (no circular imports)
"""
from __future__ import annotations

from codespec.model.expressions.base import Expression
from codespec.core.enums import ExpressionKind


class VariableReference(Expression):
    """
    Read access to a variable.
    """

    def __init__(self, variable):
        super().__init__()
        self.variable = variable
        self.kind = ExpressionKind.VARIABLE_REFERENCE.name
        self.pure = True

    def get_name(self):
        return getattr(self.variable, "name", "unknown")
