"""
codespec.core.node

CSR v1.0 Base Semantic Object

This module defines the root class for ALL CSR elements.

Every semantic construct in CSR inherits from CSRObject.

Design principles:
- Language independent
- Syntax independent
- Graph compatible
- Strongly typed via enums
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from codespec.core.ids import CSRIdentifier
from codespec.core.enums import (
    NodeKind,
    StatementKind,
    ExpressionKind,
    RelationshipKind,
)


# ------------------------------------------------------------
# Base CSR Object
# ------------------------------------------------------------

@dataclass
class CSRObject:
    """
    Root class for all CSR semantic objects.
    """

    # Identity
    id: CSRIdentifier

    # Semantic classification (exactly one of these applies)
    kind: str  # stored as string to allow unified handling

    # Human-readable name (optional for expressions)
    name: Optional[str] = None

    # Arbitrary semantic metadata
    properties: Dict[str, Any] = field(default_factory=dict)

    # Ownership structure (hierarchical containment)
    children: List["CSRObject"] = field(default_factory=list)

    # Graph relationships (semantic edges)
    relationships: List["CSRRelationship"] = field(default_factory=list)

    # --------------------------------------------------------
    # Tree operations
    # --------------------------------------------------------

    def add_child(self, child: "CSRObject") -> None:
        """
        Add a child node (ownership relationship).
        """
        self.children.append(child)

    # --------------------------------------------------------

    def add_relationship(self, relationship: "CSRRelationship") -> None:
        """
        Add a semantic relationship (graph edge).
        """
        self.relationships.append(relationship)

    # --------------------------------------------------------

    def set_property(self, key: str, value: Any) -> None:
        """
        Attach metadata to this node.
        """
        self.properties[key] = value

    # --------------------------------------------------------

    def get_property(self, key: str, default: Any = None) -> Any:
        return self.properties.get(key, default)

    # --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert CSR object to serializable dictionary.
        """

        return {
            "id": {
                "uuid": self.id.uuid,
                "kind": self.id.kind,
                "label": self.id.label,
            },
            "kind": self.kind,
            "name": self.name,
            "properties": self.properties,
            "children": [c.to_dict() for c in self.children],
            "relationships": [
                r.to_dict() for r in self.relationships
            ],
        }


# ------------------------------------------------------------
# Relationship object (defined here to avoid circular imports)
# ------------------------------------------------------------

@dataclass
class CSRRelationship:
    """
    Represents a semantic edge in the CSR graph.
    """

    kind: RelationshipKind
    source: CSRIdentifier
    target: CSRIdentifier

    properties: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.name,
            "source": self.source.uuid,
            "target": self.target.uuid,
            "properties": self.properties,
        }