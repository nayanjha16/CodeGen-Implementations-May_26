"""
codespec.model.statements.decision

CSR v1.0 Decision Statement

Represents conditional branching (if/else logic).

This is a core control-flow construct in CSR.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from codespec.model.statements.base import Statement
from codespec.core.enums import StatementKind

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.expressions.base import Expression
    from codespec.model.statements.block import Block


# ------------------------------------------------------------
# Decision Statement
# ------------------------------------------------------------

@dataclass
class Decision(Statement):
    """
    If/else conditional branching.
    """

    condition: "Expression"
    true_branch: "Block"
    false_branch: Optional["Block"] = None

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = StatementKind.DECISION.name

        # Ownership structure
        self.add_child(self.condition)
        self.add_child(self.true_branch)

        if self.false_branch:
            self.add_child(self.false_branch)

    # --------------------------------------------------------

    def has_else(self) -> bool:
        return self.false_branch is not None