"""
CSR Prompt Optimizer

Converts a full CSR graph into a compact,
LLM-friendly representation suitable for:
- codegen models (e.g., codegen-350m-multi)
- instruction-tuned LLMs
- program synthesis pipelines

Key goals:
- remove graph noise (IDs, edges, internal metadata)
- preserve semantic structure
- enforce deterministic ordering
- minimize token usage
"""

from __future__ import annotations

import json
from typing import Dict, Any, List


# ------------------------------------------------------------
# Main Optimizer
# ------------------------------------------------------------

class CSRPromptOptimizer:
    """
    Converts CSRGraph → LLM-ready prompt payload.
    """

    def __init__(self, graph):
        self.graph = graph

    # --------------------------------------------------------

    def optimize(self) -> str:
        """
        Entry point: returns JSON string for LLM prompt.
        """
        structured = self._build_semantic_view()
        return json.dumps(structured, indent=2, sort_keys=True)

    # --------------------------------------------------------

    def _build_semantic_view(self) -> Dict[str, Any]:
        """
        Converts CSR graph into compact semantic IR.
        """

        modules_out = []

        for module in self._get_modules():
            modules_out.append(self._convert_module(module))

        return {
            "csr_version": "1.0",
            "modules": modules_out
        }

    # --------------------------------------------------------

    def _convert_module(self, module) -> Dict[str, Any]:
        """
        Module → compact representation
        """

        return {
            "name": module.name,
            "classes": [
                self._convert_class(c) for c in getattr(module, "classes", [])
            ],
            "routines": [
                self._convert_routine(r) for r in getattr(module, "routines", [])
            ]
        }

    # --------------------------------------------------------

    def _convert_class(self, cls) -> Dict[str, Any]:
        """
        Class → simplified semantic structure
        """

        return {
            "name": cls.name,
            "base_classes": [b.name for b in getattr(cls, "base_classes", [])],
            "fields": [f.name for f in getattr(cls, "fields", [])],
            "methods": [
                self._convert_routine(m) for m in getattr(cls, "methods", [])
            ]
        }

    # --------------------------------------------------------

    def _convert_routine(self, routine) -> Dict[str, Any]:
        """
        Routine → execution-level summary
        """

        return {
            "name": routine.name,
            "parameters": [p.name for p in getattr(routine, "parameters", [])],
            "return_type": getattr(routine.return_type, "name", "unknown"),
            "body": self._convert_block(routine.body)
        }

    # --------------------------------------------------------

    def _convert_block(self, block) -> List[Dict[str, Any]]:
        """
        Block → ordered statement list
        """

        if not block:
            return []

        output = []

        for stmt in block.statements:
            output.append(self._convert_statement(stmt))

        return output

    # --------------------------------------------------------

    def _convert_statement(self, stmt) -> Dict[str, Any]:
        """
        Statement → normalized semantic form
        """

        kind = getattr(stmt, "kind", "UNKNOWN")

        # ---------------------------
        # Assignment
        # ---------------------------
        if kind == "ASSIGNMENT":
            return {
                "type": "assignment",
                "target": stmt.target.variable.name,
                "value": self._convert_expression(stmt.value)
            }

        # ---------------------------
        # Return
        # ---------------------------
        if kind == "RETURN":
            return {
                "type": "return",
                "value": self._convert_expression(stmt.value) if stmt.value else None
            }

        # ---------------------------
        # Decision
        # ---------------------------
        if kind == "DECISION":
            return {
                "type": "if",
                "condition": self._convert_expression(stmt.condition),
                "true": self._convert_block(stmt.true_branch),
                "false": self._convert_block(stmt.false_branch) if stmt.false_branch else None
            }

        return {
            "type": "unknown",
            "kind": kind
        }

    # --------------------------------------------------------

    def _convert_expression(self, expr) -> Dict[str, Any]:
        """
        Expression → LLM-friendly form
        """

        if expr is None:
            return {"type": "void"}

        kind = getattr(expr, "kind", "UNKNOWN")

        # ---------------------------
        # Literal
        # ---------------------------
        if kind == "LITERAL":
            return {
                "type": "literal",
                "value": expr.value
            }

        # ---------------------------
        # Variable Reference
        # ---------------------------
        if kind == "VARIABLE_REFERENCE":
            return {
                "type": "variable",
                "name": expr.variable.name
            }

        # ---------------------------
        # Binary Operation
        # ---------------------------
        if kind == "BINARY_OPERATION":
            return {
                "type": "binary",
                "op": expr.operator,
                "left": self._convert_expression(expr.left),
                "right": self._convert_expression(expr.right)
            }

        # ---------------------------
        # Call
        # ---------------------------
        if kind == "CALL":
            return {
                "type": "call",
                "function": expr.routine.name,
                "args": [self._convert_expression(a) for a in expr.arguments]
            }

        return {
            "type": "unknown_expr",
            "kind": kind
        }

    # --------------------------------------------------------

    def _get_modules(self) -> List:
        """
        Extract modules from graph.
        Assumes graph has root nodes labeled MODULE.
        """

        return [
            n for n in self.graph.nodes
            if getattr(n, "kind", None) == "MODULE"
        ]