"""
codespec.model.statements.return_

CSR v1.0 Return Statement

Represents termination of a routine with an optional value.

This is a terminal control-flow construct.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from codespec.model.statements.base import Statement
from codespec.core.enums import StatementKind

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.expressions.base import Expression


# ------------------------------------------------------------
# Return Statement
# ------------------------------------------------------------

@dataclass
class Return(Statement):
    """
    Returns control (and optionally a value) from a routine.
    """

    value: Optional["Expression"] = None

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = StatementKind.RETURN.name

        # Attach value to ownership tree if present
        if self.value:
            self.add_child(self.value)

    # --------------------------------------------------------

    def has_value(self) -> bool:
        return self.value is not None