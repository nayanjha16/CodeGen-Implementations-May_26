"""
codespec.model.entities.variable

CSR v1.0 Variable Entity

Represents a named storage location (not a reference).
"""

from __future__ import annotations

from dataclasses import dataclass

from codespec.core.node import CSRObject
from codespec.core.enums import NodeKind
from codespec.core.ids import CSRIdentifier


# ------------------------------------------------------------
# Variable Entity
# ------------------------------------------------------------

@dataclass
class Variable(CSRObject):
    """
    Represents a declared variable (storage entity).
    """

    name: str = ""
    var_type: str = "UNKNOWN"

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = NodeKind.VARIABLE.name