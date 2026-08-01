"""
============================================================
RepoCoder Studio
python_validator.py  —  v2
============================================================

Python validation utilities.

v2 changes
----------
Returns richer AST artifacts that feed semantic_artifacts in
the ApprovedRow:

  - parse_ok, function_names, class_names  (v1)
  - import_names, import_count             (new)
  - has_loop, has_conditional, has_recursion (new)
  - line_count, ast_node_count             (new)

This module does not execute untrusted Python code.
"""

import ast
from typing import Any, Dict, List


class PythonValidator:
    """
    Validates Python source code using the stdlib ast module.

    Returns a validation result dict suitable for use as a
    semantic_artifacts entry in ApprovedRow.
    """

    def validate(self, python_code: str) -> Dict[str, Any]:
        """
        Validates Python code using AST parsing.

        Returns
        -------
        dict
            Validation result with status, discovered structures,
            and rich AST metadata.
        """

        result: Dict[str, Any] = {
            "status": "FAIL",
            "parse_ok": False,
            "function_names": [],
            "class_names": [],
            "import_names": [],
            "import_count": 0,
            "has_loop": False,
            "has_conditional": False,
            "has_recursion": False,
            "line_count": 0,
            "ast_node_count": 0,
            "reason": None,
        }

        if not python_code or not python_code.strip():
            result["reason"] = "empty_python_code"
            return result

        result["line_count"] = len(python_code.splitlines())

        try:
            tree = ast.parse(python_code)
        except Exception as e:
            result["reason"] = repr(e)
            return result

        result["parse_ok"] = True

        function_names: List[str] = []
        class_names: List[str] = []
        import_names: List[str] = []
        has_loop = False
        has_conditional = False
        call_names: set = set()
        node_count = 0

        for node in ast.walk(tree):
            node_count += 1

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_names.append(node.name)

            elif isinstance(node, ast.ClassDef):
                class_names.append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    import_names.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_names.append(node.module)

            elif isinstance(node, (ast.For, ast.While)):
                has_loop = True

            elif isinstance(node, ast.If):
                has_conditional = True

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    call_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    call_names.add(node.func.attr)

        func_name_set = set(function_names)
        has_recursion = bool(func_name_set & call_names)

        result.update(
            {
                "status": "PASS",
                "function_names": function_names,
                "class_names": class_names,
                "import_names": import_names,
                "import_count": len(import_names),
                "has_loop": has_loop,
                "has_conditional": has_conditional,
                "has_recursion": has_recursion,
                "ast_node_count": node_count,
            }
        )

        return result
