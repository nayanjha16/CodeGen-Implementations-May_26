"""
codespec.core.ids

CSR v1.0 Identity System

This module provides:
- Stable globally unique identifiers (UUID)
- Human-readable labels for debugging
- Semantic kind tagging integration

Design principles:
- IDs are independent of syntax or language
- UUID ensures global uniqueness
- Labels are deterministic per graph instance
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional


# ------------------------------------------------------------
# Identity Types
# ------------------------------------------------------------

@dataclass(frozen=True)
class CSRIdentifier:
    """
    Immutable identity object for all CSR nodes.
    """

    uuid: str
    kind: str
    label: Optional[str] = None

    def __str__(self) -> str:
        return self.label or self.uuid

    def short(self) -> str:
        """
        Returns a short human-readable representation.
        """
        return self.label if self.label else self.uuid[:8]


# ------------------------------------------------------------
# ID Generator
# ------------------------------------------------------------

class CSRIdGenerator:
    """
    Generates CSR identifiers.

    Supports:
    - UUID-based generation (default)
    - Deterministic labeling per kind
    """

    def __init__(self, deterministic: bool = False):
        self.deterministic = deterministic
        self._counters = {}

    def new(self, kind: str) -> CSRIdentifier:
        """
        Create a new CSRIdentifier.

        Parameters
        ----------
        kind : str
            Semantic kind (e.g., ROUTINE, CLASS, VARIABLE)

        Returns
        -------
        CSRIdentifier
        """
        if self.deterministic:
            return self._new_deterministic(kind)

        return self._new_random(kind)

    # --------------------------------------------------------

    def _new_random(self, kind: str) -> CSRIdentifier:
        uid = str(uuid.uuid4())

        label = self._next_label(kind)

        return CSRIdentifier(
            uuid=uid,
            kind=kind,
            label=label
        )

    # --------------------------------------------------------

    def _new_deterministic(self, kind: str) -> CSRIdentifier:
        """
        Deterministic mode:
        UUID is still generated, but label is stable per instance.
        """
        namespace = uuid.NAMESPACE_OID
        uid = str(uuid.uuid4())

        label = self._next_label(kind)

        return CSRIdentifier(
            uuid=uid,
            kind=kind,
            label=label
        )

    # --------------------------------------------------------

    def _next_label(self, kind: str) -> str:
        """
        Generates sequential labels like:
        ROUTINE_000001
        CLASS_000002
        """
        count = self._counters.get(kind, 0) + 1
        self._counters[kind] = count

        return f"{kind}_{count:06d}"


# ------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------

def new_id(kind: str) -> CSRIdentifier:
    """
    Quick stateless ID generation (non-deterministic).
    """
    return CSRIdGenerator().new(kind)