"""
============================================================
RepoCoder Studio
csr_builder.py  —  v2
============================================================

Structural Representation Builder.

v2 changes (spec Chapter 8 / Decision A6)
------------------------------------------
Java structural analysis now uses Tree-sitter when available
(pip install tree-sitter tree-sitter-java).

If Tree-sitter is not installed the module falls back to the
previous regex-based analysis so the pipeline never hard-fails
in Colab environments where the package is not yet installed.

Python analysis continues to use the stdlib `ast` module — this
was already correct per the v2 spec.
"""

import ast
import re
from typing import Any, Dict, List, Tuple

from src.logger import LOG


# ============================================================
# Tree-sitter availability probe
# ============================================================

_TREE_SITTER_AVAILABLE = False
_TS_JAVA_LANGUAGE = None
_TS_PARSER = None

def _init_tree_sitter():
    global _TREE_SITTER_AVAILABLE, _TS_JAVA_LANGUAGE, _TS_PARSER
    try:
        from tree_sitter import Language, Parser
        import tree_sitter_java as tsjava
        _TS_JAVA_LANGUAGE = Language(tsjava.language())
        _TS_PARSER = Parser(_TS_JAVA_LANGUAGE)
        _TREE_SITTER_AVAILABLE = True
        LOG.info("Tree-sitter Java grammar loaded (v2 structural analysis active).")
    except Exception as e:
        LOG.warning(
            f"tree-sitter-java not available ({e}). "
            "Java structural analysis will use regex fallback."
        )
        _TREE_SITTER_AVAILABLE = False


_init_tree_sitter()


# ============================================================
# Tree-sitter helpers
# ============================================================

def _ts_collect_node_types(node, target_types: set, results: List):
    """Recursively collects Tree-sitter nodes matching target_types."""
    if node.type in target_types:
        results.append(node)
    for child in node.children:
        _ts_collect_node_types(child, target_types, results)


def _ts_node_text(node, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _build_java_structural_ts(java_code: str) -> Dict[str, Any]:
    """
    Extracts structural features from Java using Tree-sitter.
    Called only when _TREE_SITTER_AVAILABLE is True.
    """
    source_bytes = bytes(java_code, "utf-8")
    tree = _TS_PARSER.parse(source_bytes)  # type: ignore[union-attr]
    root = tree.root_node

    methods: List[str] = []
    classes: List[str] = []
    tokens: List[str] = []

    # Structural token collection
    for node in _ts_collect_generator(root):
        ntype = node.type
        if ntype == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(_ts_node_text(name_node, source_bytes))
            tokens.append("CLASS")
        elif ntype == "method_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                methods.append(_ts_node_text(name_node, source_bytes))
            tokens.append("FUNCTION")
        elif ntype in ("if_statement", "if_expression"):
            tokens.append("IF")
        elif ntype == "for_statement":
            tokens.append("FOR")
        elif ntype == "while_statement":
            tokens.append("WHILE")
        elif ntype == "return_statement":
            tokens.append("RETURN")
        elif ntype == "object_creation_expression":
            tokens.append("NEW")
        elif ntype in ("array_creation_expression", "array_initializer"):
            tokens.append("LIST")
        elif ntype == "assignment_expression":
            tokens.append("ASSIGN")
        elif ntype == "binary_expression":
            tokens.append("BINOP")

    return {
        "status": "PASS",
        "backend": "tree_sitter",
        "tokens": tokens,
        "token_count": len(tokens),
        "methods": methods,
        "classes": classes,
        "method_count": len(methods),
        "class_count": len(classes),
        "has_loop": "FOR" in tokens or "WHILE" in tokens,
        "has_conditional": "IF" in tokens,
    }


def _ts_collect_generator(node):
    """Iterative depth-first traversal of a Tree-sitter node."""
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(reversed(n.children))


# ============================================================
# Regex fallback for Java
# ============================================================

_JAVA_PATTERNS: List[Tuple[str, str]] = [
    (r"\bclass\b", "CLASS"),
    (r"\bif\s*\(", "IF"),
    (r"\bfor\s*\(", "FOR"),
    (r"\bwhile\s*\(", "WHILE"),
    (r"\breturn\b", "RETURN"),
    (r"\bnew\s+", "NEW"),
    (r"\bArrayList\b|\bList\b|\[\]", "LIST"),
    (r"\bHashMap\b|\bMap\b", "DICT"),
    (
        r"\b(?:public|private|protected)?\s*(?:static\s+)?[A-Za-z0-9_<>\[\]]+\s+[A-Za-z_][A-Za-z0-9_]*\s*\(",
        "FUNCTION",
    ),
]


def _build_java_structural_regex(java_code: str) -> Dict[str, Any]:
    tokens: List[str] = []
    java_code = java_code or ""
    for pattern, token in _JAVA_PATTERNS:
        count = len(re.findall(pattern, java_code))
        tokens.extend([token] * count)
    return {
        "status": "PASS" if tokens else "FAIL",
        "backend": "regex",
        "tokens": tokens,
        "token_count": len(tokens),
    }


# ============================================================
# Python AST patterns
# ============================================================

_PY_PATTERNS = {
    ast.FunctionDef: "FUNCTION",
    ast.AsyncFunctionDef: "FUNCTION",
    ast.ClassDef: "CLASS",
    ast.If: "IF",
    ast.For: "FOR",
    ast.While: "WHILE",
    ast.Return: "RETURN",
    ast.Call: "CALL",
    ast.Assign: "ASSIGN",
    ast.AugAssign: "AUGASSIGN",
    ast.BinOp: "BINOP",
    ast.Compare: "COMPARE",
    ast.List: "LIST",
    ast.Dict: "DICT",
}


# ============================================================
# Public builder class
# ============================================================

class CSRBuilder:
    """
    Builds structural representations for Python and Java.

    - Python: Python stdlib `ast` (deterministic, no external deps)
    - Java:   Tree-sitter when available; regex fallback otherwise

    The `similarity()` method computes Jaccard similarity over
    structural token sets — unchanged from v1.
    """

    def build_python(self, python_code: str) -> Dict[str, Any]:
        """Builds structural representation for Python via AST."""
        try:
            tree = ast.parse(python_code)
            tokens: List[str] = []
            functions: List[str] = []
            classes: List[str] = []

            for node in ast.walk(tree):
                for cls, token in _PY_PATTERNS.items():
                    if isinstance(node, cls):
                        tokens.append(token)
                        break
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            return {
                "status": "PASS",
                "backend": "ast",
                "tokens": tokens,
                "token_count": len(tokens),
                "function_names": functions,
                "class_names": classes,
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "backend": "ast",
                "tokens": [],
                "token_count": 0,
                "reason": repr(e),
            }

    def build_java(self, java_code: str) -> Dict[str, Any]:
        """
        Builds structural representation for Java.

        Uses Tree-sitter when available, regex otherwise.
        """
        if not java_code or not java_code.strip():
            return {"status": "FAIL", "backend": "none", "tokens": [], "token_count": 0}

        if _TREE_SITTER_AVAILABLE:
            try:
                return _build_java_structural_ts(java_code)
            except Exception as e:
                LOG.warning(f"Tree-sitter Java parse failed ({e}), using regex fallback.")

        return _build_java_structural_regex(java_code)

    def similarity(self, csr_a: Dict[str, Any], csr_b: Dict[str, Any]) -> float:
        """Jaccard similarity over structural token multisets (as sets)."""
        a = set(csr_a.get("tokens", []))
        b = set(csr_b.get("tokens", []))
        if not a and not b:
            return 0.0
        return len(a & b) / max(1, len(a | b))

    def tree_sitter_available(self) -> bool:
        return _TREE_SITTER_AVAILABLE
