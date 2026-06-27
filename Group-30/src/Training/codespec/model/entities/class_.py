"""
codespec.model.entities.class_

CSR v1.0 Class Entity

A Class represents an object-oriented type definition.

It supports:
- Fields (variables)
- Methods (routines)
- Inheritance relationships

This is language-agnostic (Python, C++, Java, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from codespec.core.node import CSRObject
from codespec.core.enums import NodeKind, RelationshipKind
from codespec.core.ids import CSRIdentifier
from codespec.core.node import CSRRelationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codespec.model.entities.routine import Routine
    from codespec.model.entities.variable import Variable


# ------------------------------------------------------------
# Class Entity
# ------------------------------------------------------------

@dataclass
class Class(CSRObject):
    """
    CSR representation of a class/type.
    """

    name: str = ""

    # Owned members
    fields: List["Variable"] = field(default_factory=list)
    methods: List["Routine"] = field(default_factory=list)

    # Inheritance
    base_classes: List["Class"] = field(default_factory=list)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = NodeKind.CLASS.name

    # --------------------------------------------------------
    # Field management
    # --------------------------------------------------------

    def add_field(self, field_: "Variable") -> None:
        self.fields.append(field_)
        self.add_child(field_)

    # --------------------------------------------------------
    # Method management
    # --------------------------------------------------------

    def add_method(self, method: "Routine") -> None:
        self.methods.append(method)
        self.add_child(method)

    # --------------------------------------------------------
    # Inheritance
    # --------------------------------------------------------

    def inherit_from(self, base: "Class") -> None:
        """
        Establish inheritance relationship (semantic + structural).
        """
        self.base_classes.append(base)

        # Also register graph relationship
        self.add_relationship(
            CSRRelationship(
                kind=RelationshipKind.INHERITS,
                source=self.id,
                target=base.id,
            )
        )

    # --------------------------------------------------------
    # Queries
    # --------------------------------------------------------

    def get_methods(self) -> List["Routine"]:
        return self.methods

    def get_fields(self) -> List["Variable"]:
        return self.fields

    def get_base_classes(self) -> List["Class"]:
        return self.base_classes