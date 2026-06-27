"""
codespec.model.expressions.base

CSR v1.0 Expression Base Class

Expressions represent value-producing semantic constructs.
They are the computation layer of CSR.
"""
from __future__ import annotations

from typing import Optional
from codespec.core.node import CSRObject


class Expression(CSRObject):
    """
    Base class for all expressions (NO dataclass).
    """

    def __init__(self):
        super().__init__()
        self.inferred_type: Optional[str] = None
        self.pure: bool = True
