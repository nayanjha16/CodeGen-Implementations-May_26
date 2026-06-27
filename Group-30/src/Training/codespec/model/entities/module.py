"""
codespec.model.entities.module

CSR v1.0 Module Entity

A Module represents a top-level program container.
It corresponds to:
- Python file
- C++ translation unit
- Java source file

It is the root entry point for CSR construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from codespec.core.node import CSRObject
from codespec.core.ids import CSRIdentifier
from codespec.core.enums import NodeKind


# Forward references (semantic entities)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from codespec.model.entities.class_ import Class
    from codespec.model.entities.routine import Routine
    from codespec.model.entities.variable import Variable


# ------------------------------------------------------------
# Module Entity
# ------------------------------------------------------------

@dataclass
class Module(CSRObject):
    """
    Top-level container for all CSR entities.
    """

    name: str = ""

    # Owned entities
    classes: List["Class"] = field(default_factory=list)
    routines: List["Routine"] = field(default_factory=list)
    variables: List["Variable"] = field(default_factory=list)

    # --------------------------------------------------------

    def __post_init__(self):
        self.kind = NodeKind.MODULE.name

    # --------------------------------------------------------
    # Class management
    # --------------------------------------------------------

    def add_class(self, cls: "Class") -> None:
        self.classes.append(cls)
        self.add_child(cls)

    # --------------------------------------------------------
    # Routine management
    # --------------------------------------------------------

    def add_routine(self, routine: "Routine") -> None:
        self.routines.append(routine)
        self.add_child(routine)

    # --------------------------------------------------------
    # Variable management
    # --------------------------------------------------------

    def add_variable(self, variable: "Variable") -> None:
        self.variables.append(variable)
        self.add_child(variable)

    # --------------------------------------------------------
    # Queries
    # --------------------------------------------------------

    def get_all_routines(self) -> List["Routine"]:
        return self.routines

    def get_all_classes(self) -> List["Class"]:
        return self.classes

    def get_all_variables(self) -> List["Variable"]:
        return self.variables