"""
============================================================
RepoCoder Studio
java_validator.py — v2.2 Batch 1
============================================================

Java validation utilities.

Responsibilities
----------------
- Strip generation artifacts.
- Ensure code can be compiled as a Java compilation unit.
- Compile with javac.
- Parse validated Java using Tree-sitter when available.
- Return parser-derived structural artifacts for ApprovedRow storage.

The validator does not execute untrusted Java programs.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import CONFIG, AppConfig
from src.logger import LOG


# ============================================================
# Robust Tree-sitter Java initialization
# ============================================================

_TS_AVAILABLE = False
_TS_PARSER = None
_TS_INIT_ERROR: Optional[str] = None


def _init_tree_sitter_java() -> None:
    global _TS_AVAILABLE, _TS_PARSER, _TS_INIT_ERROR
    try:
        from tree_sitter import Language, Parser  # type: ignore
        import tree_sitter_java as tsjava  # type: ignore

        language = Language(tsjava.language())

        try:
            parser = Parser(language)
        except TypeError:
            parser = Parser()
            parser.set_language(language)

        _TS_PARSER = parser
        _TS_AVAILABLE = True
        _TS_INIT_ERROR = None
    except Exception as exc:  # pragma: no cover - environment dependent
        _TS_AVAILABLE = False
        _TS_PARSER = None
        _TS_INIT_ERROR = repr(exc)


_init_tree_sitter_java()


def _walk_ts(node):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def _node_text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _extract_java_artifacts_ts(java_code: str) -> Dict[str, Any]:
    """Extracts Java parser artifacts using Tree-sitter."""
    result: Dict[str, Any] = {
        "backend": "tree_sitter" if _TS_AVAILABLE else "tree_sitter_unavailable",
        "tree_sitter_available": _TS_AVAILABLE,
        "tree_sitter_error": _TS_INIT_ERROR,
        "parse_ok": False,
        "has_parse_error": False,
        "class_names": [],
        "method_names": [],
        "constructor_names": [],
        "import_names": [],
        "package_name": None,
        "class_count": 0,
        "method_count": 0,
        "constructor_count": 0,
        "import_count": 0,
        "has_loop": False,
        "has_conditional": False,
        "parse_tree_node_count": 0,
    }

    if not _TS_AVAILABLE or _TS_PARSER is None:
        return result

    try:
        src = java_code.encode("utf-8", errors="replace")
        tree = _TS_PARSER.parse(src)
        root = tree.root_node
        result["has_parse_error"] = bool(getattr(root, "has_error", False))
        result["parse_ok"] = not result["has_parse_error"]

        class_names: List[str] = []
        method_names: List[str] = []
        constructor_names: List[str] = []
        import_names: List[str] = []

        for node in _walk_ts(root):
            result["parse_tree_node_count"] += 1
            nt = node.type

            if nt == "package_declaration":
                result["package_name"] = _node_text(src, node)
            elif nt == "import_declaration":
                import_names.append(_node_text(src, node))
            elif nt == "class_declaration":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    class_names.append(_node_text(src, name_node))
            elif nt == "method_declaration":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    method_names.append(_node_text(src, name_node))
            elif nt == "constructor_declaration":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    constructor_names.append(_node_text(src, name_node))
            elif nt in {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}:
                result["has_loop"] = True
            elif nt == "if_statement":
                result["has_conditional"] = True

        result.update({
            "class_names": class_names,
            "method_names": method_names,
            "constructor_names": constructor_names,
            "import_names": import_names,
            "class_count": len(class_names),
            "method_count": len(method_names),
            "constructor_count": len(constructor_names),
            "import_count": len(import_names),
        })
        return result

    except Exception as exc:
        result["backend"] = "tree_sitter_error"
        result["tree_sitter_error"] = repr(exc)
        return result


class JavaValidator:
    """Validates Java source code using javac and Tree-sitter."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config

    def tree_sitter_available(self) -> bool:
        return _TS_AVAILABLE

    def tree_sitter_error(self) -> Optional[str]:
        return _TS_INIT_ERROR

    def strip_generation_artifacts(self, text: str) -> str:
        """Removes markdown fences and common model-output artifacts."""
        if not text:
            return ""
        text = re.sub(r"```(?:java)?", "", text, flags=re.IGNORECASE)
        text = text.replace("```", "")
        return text.strip()

    def detect_public_class_name(self, java_code: str) -> Optional[str]:
        """Returns public class name if present, else any class name."""
        public_match = re.search(r"\bpublic\s+class\s+([A-Za-z_][A-Za-z0-9_]*)", java_code)
        if public_match:
            return public_match.group(1)

        class_match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", java_code)
        if class_match:
            return class_match.group(1)

        return None

    def ensure_compilation_unit(self, java_code: str, default_class_name: str = "Main") -> Tuple[str, str, Dict[str, Any]]:
        """
        Ensures Java source can be compiled from a single .java file.

        If a class is missing, the snippet is wrapped in a public class. This is
        a syntax-preserving wrapper step used only to enable compilation checks.
        """
        original = java_code or ""
        java_code = self.strip_generation_artifacts(original)
        class_name = self.detect_public_class_name(java_code)
        repair_metadata = {
            "stripped_generation_artifacts": original != java_code,
            "wrapped_missing_class": False,
            "detected_class_name": class_name,
        }

        if class_name:
            return java_code, class_name, repair_metadata

        wrapped = f"public class {default_class_name} {{\n{java_code}\n}}\n"
        repair_metadata["wrapped_missing_class"] = True
        repair_metadata["detected_class_name"] = default_class_name
        return wrapped, default_class_name, repair_metadata

    def validate(self, java_code: str) -> Dict[str, Any]:
        """Compiles Java code and extracts parser-derived artifacts."""
        if not java_code or not java_code.strip():
            return {
                "status": "FAIL",
                "compiles": False,
                "class_name": None,
                "reason": "empty_java_code",
                "stderr": "",
                "stdout": "",
                "normalized_compilation_unit": "",
                "structural_artifacts": {},
            }

        compilation_unit, class_name, repair_metadata = self.ensure_compilation_unit(java_code)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            java_file = tmp_path / f"{class_name}.java"
            java_file.write_text(compilation_unit, encoding="utf-8")

            try:
                proc = subprocess.run(
                    ["javac", str(java_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.config.validation.java_compile_timeout_seconds,
                )

                compiles = proc.returncode == 0
                artifacts: Dict[str, Any] = {}
                if compiles:
                    artifacts = _extract_java_artifacts_ts(compilation_unit)

                return {
                    "status": "PASS" if compiles else "FAIL",
                    "compiles": compiles,
                    "class_name": class_name,
                    "reason": None if compiles else "javac_error",
                    "stderr": proc.stderr[-3000:],
                    "stdout": proc.stdout[-3000:],
                    "normalized_compilation_unit": compilation_unit,
                    "repair_metadata": repair_metadata,
                    "structural_artifacts": artifacts,
                    "tree_sitter_available": _TS_AVAILABLE,
                    "tree_sitter_error": _TS_INIT_ERROR,
                }

            except FileNotFoundError:
                return {
                    "status": "NOT_FEASIBLE",
                    "compiles": False,
                    "class_name": class_name,
                    "reason": "javac_not_found",
                    "stderr": "javac not found",
                    "stdout": "",
                    "normalized_compilation_unit": compilation_unit,
                    "repair_metadata": repair_metadata,
                    "structural_artifacts": {},
                    "tree_sitter_available": _TS_AVAILABLE,
                    "tree_sitter_error": _TS_INIT_ERROR,
                }

            except subprocess.TimeoutExpired:
                return {
                    "status": "FAIL",
                    "compiles": False,
                    "class_name": class_name,
                    "reason": "javac_timeout",
                    "stderr": "javac timed out",
                    "stdout": "",
                    "normalized_compilation_unit": compilation_unit,
                    "repair_metadata": repair_metadata,
                    "structural_artifacts": {},
                    "tree_sitter_available": _TS_AVAILABLE,
                    "tree_sitter_error": _TS_INIT_ERROR,
                }

            except Exception as exc:
                return {
                    "status": "FAIL",
                    "compiles": False,
                    "class_name": class_name,
                    "reason": repr(exc),
                    "stderr": repr(exc),
                    "stdout": "",
                    "normalized_compilation_unit": compilation_unit,
                    "repair_metadata": repair_metadata,
                    "structural_artifacts": {},
                    "tree_sitter_available": _TS_AVAILABLE,
                    "tree_sitter_error": _TS_INIT_ERROR,
                }
