"""
codespec.model.statements.assignment

CSR v1.0 Assignment Statement

Represents semantic assignment of a value to a target.

All assignment variants are normalized into:
    target <- value
"""

from __future__ import annotations

from dataclasses import dataclass

from codespec.model.statements.base import Statement
from codespec.core.enums import StatementKind
from codespec.core.node import CSRRelationship
from codespec.core.enums import RelationshipKind

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.expressions.base import Expression
    from codespec.model.expressions.variable_reference import VariableReference


# ------------------------------------------------------------
# Assignment Statement
# ------------------------------------------------------------

@dataclass
class Assignment(Statement):
    """
    CSR representation of assignment operation.
    """

    target: "VariableReference"
    value: "Expression"

    operator: str = "="  # normalized operator (always "=" in CSR v1)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = StatementKind.ASSIGNMENT.name

        # Register semantic WRITE relationship
        self.add_relationship(
            CSRRelationship(
                kind=RelationshipKind.WRITES,
                source=self.target.id,
                target=self.target.id,
            )
        )

    # --------------------------------------------------------

    def normalize(self) -> None:
        """
        Ensures assignment is in canonical form.

        Future: convert +=, -=, etc. into binary expansion.
        """
        self.operator = "="