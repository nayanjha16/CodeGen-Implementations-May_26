"""
codespec.core.graph

CSR v1.0 Graph Container

This module defines the central graph structure that holds
all CSR objects and relationships.

It is responsible for:
- Node registration
- Fast lookup
- Relationship indexing
- Graph traversal utilities

Design principles:
- No parsing logic
- No language awareness
- Pure semantic graph container
"""

from __future__ import annotations

from typing import Dict, List, Optional, Iterable, Set

from codespec.core.ids import CSRIdentifier
from codespec.core.node import CSRObject, CSRRelationship
from codespec.core.enums import RelationshipKind


# ------------------------------------------------------------
# CSR Graph
# ------------------------------------------------------------

class CSRGraph:
    """
    Central container for all CSR objects.
    """

    def __init__(self):
        # UUID → CSRObject
        self._nodes: Dict[str, CSRObject] = {}

        # Root nodes (Program, Module, etc.)
        self._roots: List[CSRObject] = []

        # Global relationship index
        self._relationships: List[CSRRelationship] = []

    # --------------------------------------------------------
    # Node Management
    # --------------------------------------------------------

    def add_node(self, node: CSRObject, is_root: bool = False) -> None:
        """
        Register a node in the graph.
        """
        self._nodes[node.id.uuid] = node

        if is_root:
            self._roots.append(node)

    # --------------------------------------------------------

    def get_node(self, uuid: str) -> Optional[CSRObject]:
        """
        Retrieve a node by UUID.
        """
        return self._nodes.get(uuid)

    # --------------------------------------------------------

    def all_nodes(self) -> Iterable[CSRObject]:
        """
        Iterate over all nodes in the graph.
        """
        return self._nodes.values()

    # --------------------------------------------------------
    # Relationship Management
    # --------------------------------------------------------

    def add_relationship(self, relationship: CSRRelationship) -> None:
        """
        Add a semantic relationship to the graph.
        """
        self._relationships.append(relationship)

        # Attach relationship to source node (if present)
        source = self._nodes.get(relationship.source.uuid)
        if source:
            source.add_relationship(relationship)

    # --------------------------------------------------------

    def get_relationships(
        self,
        kind: Optional[RelationshipKind] = None
    ) -> List[CSRRelationship]:
        """
        Retrieve relationships, optionally filtered by kind.
        """
        if kind is None:
            return self._relationships

        return [r for r in self._relationships if r.kind == kind]

    # --------------------------------------------------------
    # Traversal Utilities
    # --------------------------------------------------------

    def children_of(self, node: CSRObject) -> List[CSRObject]:
        """
        Get direct children (ownership tree).
        """
        return node.children

    # --------------------------------------------------------

    def outgoing_relationships(
        self,
        node: CSRObject
    ) -> List[CSRRelationship]:
        """
        Get all outgoing relationships from a node.
        """
        return [
            r for r in self._relationships
            if r.source.uuid == node.id.uuid
        ]

    # --------------------------------------------------------

    def incoming_relationships(
        self,
        node: CSRObject
    ) -> List[CSRRelationship]:
        """
        Get all incoming relationships to a node.
        """
        return [
            r for r in self._relationships
            if r.target.uuid == node.id.uuid
        ]

    # --------------------------------------------------------
    # Graph Utilities
    # --------------------------------------------------------

    def find_by_kind(self, kind: str) -> List[CSRObject]:
        """
        Find all nodes of a given semantic kind.
        """
        return [
            n for n in self._nodes.values()
            if n.kind == kind
        ]

    # --------------------------------------------------------

    def roots(self) -> List[CSRObject]:
        """
        Return root nodes (entry points of program structure).
        """
        return self._roots

    # --------------------------------------------------------

    def size(self) -> int:
        """
        Number of nodes in the graph.
        """
        return len(self._nodes)

    # --------------------------------------------------------

    def relationship_count(self) -> int:
        """
        Number of relationships in the graph.
        """
        return len(self._relationships)

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialize entire graph.
        """
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "relationships": [
                {
                    "kind": r.kind.name,
                    "source": r.source.uuid,
                    "target": r.target.uuid,
                    "properties": r.properties,
                }
                for r in self._relationships
            ],
        }