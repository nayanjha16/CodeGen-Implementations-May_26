"""
codespec.model.expressions.base

CSR v1.0 Expression Base Class

Expressions represent value-producing semantic constructs.
They are the computation layer of CSR.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any

from codespec.core.node import CSRObject
from codespec.core.enums import ExpressionKind
from codespec.core.ids import CSRIdentifier


# ------------------------------------------------------------
# Expression Base Class
# ------------------------------------------------------------

@dataclass
class Expression(CSRObject):
    """
    Base class for all CSR expressions.
    """

    # Optional inferred/static type (resolved later in pipeline)
    inferred_type: Optional[str] = None

    # Indicates if expression is pure (no side effects)
    pure: bool = True

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = ExpressionKind.LITERAL.name

    # --------------------------------------------------------
    # Semantic helpers
    # --------------------------------------------------------

    def has_side_effects(self) -> bool:
        """
        Returns True if expression modifies state.
        """
        return not self.pure