"""
codespec.model.entities.routine

CSR v1.0 Routine Entity

A Routine represents an executable unit of behavior:
- Function (Python)
- Method (C++)
- Procedure (general)

It is the core unit of execution in CSR.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Any

from codespec.core.node import CSRObject, CSRRelationship
from codespec.core.enums import NodeKind, RelationshipKind
from codespec.core.ids import CSRIdentifier

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.entities.variable import Variable
    from codespec.model.entities.class_ import Class
    from codespec.model.statements.block import Block
    from codespec.model.entities.type import Type


# ------------------------------------------------------------
# Routine Entity
# ------------------------------------------------------------

@dataclass
class Routine(CSRObject):
    """
    CSR representation of a function/method/procedure.
    """

    name: str = ""

    # Parameters
    parameters: List["Variable"] = field(default_factory=list)

    # Return type (semantic type, not language-specific)
    return_type: Optional["Type"] = None

    # Body (block of statements)
    body: Optional["Block"] = None

    # Parent class (if method)
    parent_class: Optional["Class"] = None

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = NodeKind.ROUTINE.name

    # --------------------------------------------------------
    # Parameter management
    # --------------------------------------------------------

    def add_parameter(self, param: "Variable") -> None:
        self.parameters.append(param)
        self.add_child(param)

    # --------------------------------------------------------
    # Body management
    # --------------------------------------------------------

    def set_body(self, block: "Block") -> None:
        self.body = block
        self.add_child(block)

    # --------------------------------------------------------
    # Return type
    # --------------------------------------------------------

    def set_return_type(self, return_type: "Type") -> None:
        self.return_type = return_type

    # --------------------------------------------------------
    # Call relationship helper
    # --------------------------------------------------------

    def calls(self, other: "Routine") -> None:
        """
        Declare that this routine calls another routine.
        """
        self.add_relationship(
            CSRRelationship(
                kind=RelationshipKind.CALLS,
                source=self.id,
                target=other.id,
            )
        )