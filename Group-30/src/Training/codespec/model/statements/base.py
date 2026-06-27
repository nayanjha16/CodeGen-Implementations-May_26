"""
codespec.model.statements.block

CSR v1.0 Block Statement

A Block represents a scoped sequence of statements.

It is used for:
- function bodies
- loop bodies
- conditional branches
- exception handling blocks

Blocks define:
- lexical scope
- execution order
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Any
from codespec.core.node import CSRObject
from codespec.core.enums import StatementKind
from codespec.core.ids import CSRIdentifier

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.statements.base import Statement

"""
codespec.model.statements.base

Safe CSR Statement Base Class
(no circular dependencies)
"""


# ------------------------------------------------------------
# Statement Base Class
# ------------------------------------------------------------

@dataclass
class Statement(CSRObject):
    """
    Base class for all CSR statements.
    """

    source_hint: Optional[str] = None
    order_index: Optional[int] = None

    def __post_init__(self):
        # SAFE default only
        self.kind = "STATEMENT"

    # --------------------------------------------------------

    def is_control_flow(self) -> bool:
        return self.kind in {
            StatementKind.LOOP.name,
            StatementKind.DECISION.name,
            StatementKind.RETURN.name,
        }

    def is_terminal(self) -> bool:
        return self.kind in {
            StatementKind.RETURN.name,
            StatementKind.BREAK.name,
            StatementKind.CONTINUE.name,
        }
        

# ------------------------------------------------------------
# Block Statement
# ------------------------------------------------------------

@dataclass
class Block(CSRObject):
    """
    Ordered container of statements.
    """

    statements: List["Statement"] = field(default_factory=list)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = StatementKind.BLOCK.name

    # --------------------------------------------------------
    # Statement management
    # --------------------------------------------------------

    def add_statement(self, stmt: "Statement") -> None:
        """
        Add a statement in execution order.
        """
        self.statements.append(stmt)
        self.add_child(stmt)

    # --------------------------------------------------------

    def extend(self, stmts: List["Statement"]) -> None:
        """
        Add multiple statements preserving order.
        """
        for s in stmts:
            self.add_statement(s)

    # --------------------------------------------------------

    def get_statements(self) -> List["Statement"]:
        return self.statements
