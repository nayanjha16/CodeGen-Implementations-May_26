 """
codespec.model.expressions.call

CSR v1.0 Call Expression

Represents invocation of a routine (function/method).

This is a key bridge between:
- expressions
- routines
- inter-procedural graph analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from codespec.model.expressions.base import Expression
from codespec.core.enums import ExpressionKind
from codespec.core.node import CSRRelationship
from codespec.core.enums import RelationshipKind

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.entities.routine import Routine
    from codespec.model.expressions.base import Expression


# ------------------------------------------------------------
# Call Expression
# ------------------------------------------------------------

class Call(Expression):
    """
    Function or method invocation.
    """

    routine: "Routine"
    arguments: List["Expression"] = field(default_factory=list)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = ExpressionKind.CALL.name
        self.pure = False  # calls may have side effects

        # Attach arguments to ownership tree
        for arg in self.arguments:
            self.add_child(arg)

        # Register CALLS relationship
        self.add_relationship(
            CSRRelationship(
                kind=RelationshipKind.CALLS,
                source=self.id,
                target=self.routine.id,
            )
        )

    # --------------------------------------------------------

    def add_argument(self, arg: "Expression") -> None:
        self.arguments.append(arg)
        self.add_child(arg)
