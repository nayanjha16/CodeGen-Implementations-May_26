"""
============================================================
RepoCoder Studio
repair_engine.py — v2.3 Batch 2
============================================================

Validation-Oriented Repair Engine.

Design role
-----------
The RepairEngine implements the bounded feedback loop required by the
v2 design. It never approves rows directly. It receives a failed
CandidateRow component, produces one repaired candidate, and returns
structured repair history. The ValidationEngine owns the three-attempt
loop and decides whether a row is approved or rejected.

Batch 2 changes
---------------
1. Fixes Java repair syntax issue from the previous intermediate file.
2. Keeps deterministic repair first when teacher repair is disabled.
3. Uses TeacherEngine for validation-guided repair when enabled.
4. Records structured repair history for every attempt.
5. Avoids destructive modification of validated modalities.
"""

from __future__ import annotations

import re
import textwrap
from typing import Any, Dict, Tuple

from src.config import CONFIG, AppConfig
from src.schemas import CandidateRow
from src.python_validator import PythonValidator
from src.java_validator import JavaValidator
from src.teacher_engine import TeacherEngine


class RepairEngine:
    """Component-level repair engine for CandidateRow objects."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.python_validator = PythonValidator()
        self.java_validator = JavaValidator(config)
        self.teacher = TeacherEngine(config)

    def _teacher_enabled(self) -> bool:
        return bool(getattr(self.config.validation, "enable_teacher_repair", False))

    def _history(
        self,
        row: CandidateRow,
        component: str,
        attempt_number: int,
        reason: str,
        method: str,
        outcome: str,
        extra: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "corpus_id": row.corpus_id,
            "component": component,
            "attempt_number": attempt_number,
            "failure_reason": reason,
            "repair_method": method,
            "outcome": outcome,
            **(extra or {}),
        }

    # --------------------------------------------------------
    # Natural language repair / generation
    # --------------------------------------------------------

    def repair_natural_language(
        self,
        row: CandidateRow,
        reason: str,
        attempt_number: int = 1,
    ) -> Tuple[CandidateRow, Dict[str, Any]]:
        """Repairs missing or weak natural language."""
        feedback = {
            "component": "natural_language",
            "reason": reason,
            "attempt": attempt_number,
        }

        if self._teacher_enabled():
            result = self.teacher.generate_natural_language(
                python_code=row.python_code,
                java_code=row.java_code,
                feedback=feedback,
            )
            nl = (result.get("text") or "").strip()
            method = "teacher_generate_natural_language"
            extra = {
                "teacher_status": result.get("status"),
                "teacher_reason": result.get("reason"),
                "fallback_used": result.get("fallback_used", False),
            }
        else:
            if attempt_number == 1:
                py_result = self.python_validator.validate(row.python_code)
                functions = py_result.get("function_names", [])
                if functions:
                    nl = f"Compute the result implemented by the function {functions[0]}."
                else:
                    nl = "Compute the result implemented by the provided program."
                method = "deterministic_function_name_summary"
            elif attempt_number == 2:
                nl = "Implement the algorithm described by the provided source code."
                method = "deterministic_generic_summary"
            else:
                class_match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", row.java_code or "")
                if class_match:
                    nl = f"Implement the programming task represented by the class {class_match.group(1)}."
                else:
                    nl = "Implement the programming task represented by the provided source code."
                method = "deterministic_java_class_summary"
            extra = {"teacher_status": "DISABLED"}

        repaired = CandidateRow(
            corpus_id=row.corpus_id,
            dataset=row.dataset,
            dataset_record_id=row.dataset_record_id,
            split=row.split,
            natural_language=nl,
            python_code=row.python_code,
            java_code=row.java_code,
            metadata={
                **row.metadata,
                "nl_repaired": True,
                f"nl_repair_attempt_{attempt_number}": method,
            },
            provenance={
                **row.provenance,
                f"nl_repair_{attempt_number}": method,
            },
        )

        return repaired, self._history(row, "Natural Language", attempt_number, reason, method, "generated", extra)

    # --------------------------------------------------------
    # Python repair / generation
    # --------------------------------------------------------

    def repair_python(
        self,
        row: CandidateRow,
        reason: str,
        attempt_number: int = 1,
    ) -> Tuple[CandidateRow, Dict[str, Any]]:
        """Repairs invalid Python or regenerates Python when teacher repair is enabled."""
        feedback = {
            "component": "python",
            "reason": reason,
            "attempt": attempt_number,
        }

        if self._teacher_enabled():
            result = self.teacher.generate_python(
                natural_language=row.natural_language or "",
                java_code=row.java_code,
                feedback=feedback,
            )
            repaired_code = (result.get("text") or "").strip()
            method = "teacher_generate_python"
            extra = {
                "teacher_status": result.get("status"),
                "teacher_reason": result.get("reason"),
            }
        else:
            original = row.python_code or ""
            if attempt_number == 1:
                repaired_code = textwrap.dedent(original).strip()
                method = "dedent"
            elif attempt_number == 2:
                dedented = textwrap.dedent(original).strip()
                indented = "\n".join("    " + line for line in dedented.splitlines())
                repaired_code = f"def _solution():\n{indented}\n"
                method = "function_wrap"
            else:
                dedented = textwrap.dedent(original).strip()
                indented = "\n".join("        " + line for line in dedented.splitlines())
                repaired_code = "class _Solution:\n    def solve(self):\n" + indented + "\n"
                method = "class_wrap"
            extra = {"teacher_status": "DISABLED"}

        repaired = CandidateRow(
            corpus_id=row.corpus_id,
            dataset=row.dataset,
            dataset_record_id=row.dataset_record_id,
            split=row.split,
            natural_language=row.natural_language,
            python_code=repaired_code,
            java_code=row.java_code,
            metadata={
                **row.metadata,
                "python_repaired": True,
                f"python_repair_attempt_{attempt_number}": method,
            },
            provenance={
                **row.provenance,
                f"python_repair_{attempt_number}": method,
            },
        )

        return repaired, self._history(row, "Python", attempt_number, reason, method, "generated", extra)

    # --------------------------------------------------------
    # Java repair / generation
    # --------------------------------------------------------

    def repair_java_wrapper(
        self,
        row: CandidateRow,
        reason: str,
        attempt_number: int = 1,
    ) -> Tuple[CandidateRow, Dict[str, Any]]:
        """Repairs invalid Java or regenerates Java when teacher repair is enabled."""
        feedback = {
            "component": "java",
            "reason": reason,
            "attempt": attempt_number,
        }

        if self._teacher_enabled():
            result = self.teacher.generate_java(
                natural_language=row.natural_language or "",
                python_code=row.python_code,
                feedback=feedback,
            )
            java_code = (result.get("text") or "").strip()
            class_name = None
            method = "teacher_generate_java"
            extra = {
                "teacher_status": result.get("status"),
                "teacher_reason": result.get("reason"),
            }
        else:
            original = row.java_code or ""
            if attempt_number == 1:
                java_code, class_name, repair_meta = self.java_validator.ensure_compilation_unit(original)
                method = "ensure_compilation_unit"
            elif attempt_number == 2:
                java_code, class_name, repair_meta = self.java_validator.ensure_compilation_unit(
                    original,
                    default_class_name="Solution",
                )
                method = "force_solution_class"
            else:
                inner = textwrap.dedent(original).strip()
                java_code = (
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "    }\n\n"
                    "    // Original candidate code retained for diagnostics.\n"
                    f"    {inner.replace(chr(10), chr(10) + '    ')}\n"
                    "}\n"
                )
                class_name = "Main"
                repair_meta = {"wrapped_missing_class": True, "forced_main_wrapper": True}
                method = "main_class_wrap"
            extra = {"teacher_status": "DISABLED", "java_class_name": class_name, "repair_metadata": repair_meta}

        repaired = CandidateRow(
            corpus_id=row.corpus_id,
            dataset=row.dataset,
            dataset_record_id=row.dataset_record_id,
            split=row.split,
            natural_language=row.natural_language,
            python_code=row.python_code,
            java_code=java_code,
            metadata={
                **row.metadata,
                "java_repaired": True,
                f"java_repair_attempt_{attempt_number}": method,
                **({"java_class_name": class_name} if class_name else {}),
            },
            provenance={
                **row.provenance,
                f"java_repair_{attempt_number}": method,
            },
        )

        return repaired, self._history(row, "Java", attempt_number, reason, method, "generated", extra)
