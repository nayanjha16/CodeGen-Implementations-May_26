"""
codespec.core.enums

CSR v1.0 Canonical Vocabulary

This module defines all standardized semantic categories
used across the CSR system.

Design rules:
- NO free-text strings in the system
- All semantic classification MUST use these enums
- Extensible only via new versions of CSR spec
"""

from enum import Enum, auto


# ============================================================
# 1. NODE KINDS (Top-level semantic objects)
# ============================================================

class NodeKind(Enum):
    PROGRAM = auto()
    MODULE = auto()
    NAMESPACE = auto()
    CLASS = auto()
    INTERFACE = auto()
    ROUTINE = auto()
    PARAMETER = auto()
    VARIABLE = auto()
    FIELD = auto()
    PROPERTY = auto()
    ENUMERATION = auto()
    ENUMERATION_VALUE = auto()
    TYPE = auto()
    PACKAGE = auto()


# ============================================================
# 2. STATEMENTS (Control flow / actions)
# ============================================================

class StatementKind(Enum):
    ASSIGNMENT = auto()
    RETURN = auto()
    LOOP = auto()
    DECISION = auto()
    SWITCH = auto()
    BREAK = auto()
    CONTINUE = auto()
    THROW = auto()
    TRY = auto()
    CATCH = auto()
    EXPRESSION = auto()
    BLOCK = auto()


# ============================================================
# 3. EXPRESSIONS (Value-producing constructs)
# ============================================================

class ExpressionKind(Enum):
    LITERAL = auto()
    VARIABLE_REFERENCE = auto()
    FIELD_REFERENCE = auto()
    ARRAY_ACCESS = auto()
    MEMBER_ACCESS = auto()
    CALL = auto()
    OBJECT_CREATION = auto()
    BINARY_OPERATION = auto()
    UNARY_OPERATION = auto()
    CONDITIONAL = auto()
    LAMBDA = auto()
    CAST = auto()


# ============================================================
# 4. RELATIONSHIPS (Graph edges)
# ============================================================

class RelationshipKind(Enum):
    OWNS = auto()
    CONTAINS = auto()
    CALLS = auto()
    USES = auto()
    RETURNS = auto()
    THROWS = auto()
    INHERITS = auto()
    IMPLEMENTS = auto()
    CREATES = auto()
    READS = auto()
    WRITES = auto()
    DEPENDS_ON = auto()


# ============================================================
# 5. PRIMITIVE TYPES (Canonical type system)
# ============================================================

class PrimitiveType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    STRING = auto()
    VOID = auto()
    UNKNOWN = auto()