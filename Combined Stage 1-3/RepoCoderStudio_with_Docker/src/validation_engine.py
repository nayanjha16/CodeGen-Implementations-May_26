"""
============================================================
RepoCoder Studio
validation_engine.py — v2.4 Batch 2.1
============================================================

Corpus Validation Engine.

Design role
-----------
Converts CandidateRow objects into ApprovedRow or RejectedRow objects.
This module is the relationship-level quality gate. It does not load
datasets, align evidence pools, train models, or evaluate predictions.

Batch 2 improvements
--------------------
1. Uses post-repair Python and Java validation outputs as authoritative.
2. Stores Python AST metadata and Java parse-tree metadata as first-class
   ApprovedRow fields.
3. Stores CSR score only; CSR token bags are not stored in the corpus.
4. Preserves validation diagnostics for rejected rows.
5. Adds Tree-sitter backend visibility to ApprovedRow metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.config import CONFIG, AppConfig
from src.schemas import CandidateRow, ApprovedRow, RejectedRow, dataclass_to_dict
from src.storage import ProjectStorageManager
from src.python_validator import PythonValidator
from src.java_validator import JavaValidator
from src.trusted_test_builder import TrustedTestBuilder
from src.csr_builder import CSRBuilder
from src.repair_engine import RepairEngine
from src.logger import LOG, SectionPrinter, SummaryPrinter


class ValidationEngine:
    """Runs full corpus validation on CandidateRows."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.python_validator = PythonValidator()
        self.java_validator = JavaValidator(config)
        self.test_builder = TrustedTestBuilder(config)
        self.csr_builder = CSRBuilder()
        self.repair_engine = None  # lazy; avoids loading Teacher during validation unless repair is explicitly enabled

    # --------------------------------------------------------
    # Natural language validation
    # --------------------------------------------------------

    def validate_natural_language(self, row: CandidateRow) -> Dict[str, Any]:
        nl = (row.natural_language or "").strip()
        if not nl:
            return {"status": "FAIL", "reason": "missing_natural_language"}
        if len(nl.split()) < self.config.corpus.min_nl_words:
            return {"status": "FAIL", "reason": "too_short", "word_count": len(nl.split())}
        leakage_patterns = ["def ", "public class", "System.out", "import ", "class GFG"]
        if any(pattern in nl for pattern in leakage_patterns):
            return {"status": "FAIL", "reason": "code_leakage"}
        return {"status": "PASS", "reason": None, "word_count": len(nl.split())}

    # --------------------------------------------------------
    # Execution validation
    # --------------------------------------------------------

    def validate_execution(self, row: CandidateRow, trusted_tests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder execution validation hook.

        The v2 design allows NOT_FEASIBLE when no trusted logical tests exist.
        A full language-neutral execution harness belongs to the next trusted
        test execution batch.
        """
        tests = trusted_tests.get("tests", []) if isinstance(trusted_tests, dict) else []
        if not tests:
            return {"status": "NOT_FEASIBLE", "reason": "no_trusted_tests", "num_tests": 0}
        return {
            "status": "NOT_FEASIBLE",
            "reason": "generic_cross_language_harness_not_enabled",
            "num_tests": len(tests),
        }

    # --------------------------------------------------------
    # Artifact assembly
    # --------------------------------------------------------

    def _build_python_ast_artifact(self, py_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "backend": "ast",
            "parse_ok": py_result.get("parse_ok", False),
            "function_names": py_result.get("function_names", []),
            "class_names": py_result.get("class_names", []),
            "import_names": py_result.get("import_names", []),
            "import_count": py_result.get("import_count", 0),
            "has_loop": py_result.get("has_loop", False),
            "has_conditional": py_result.get("has_conditional", False),
            "has_recursion": py_result.get("has_recursion", False),
            "line_count": py_result.get("line_count", 0),
            "ast_node_count": py_result.get("ast_node_count", 0),
        }

    def _build_java_parse_tree_artifact(self, java_result: Dict[str, Any]) -> Dict[str, Any]:
        artifacts = java_result.get("structural_artifacts", {}) or {}
        return {
            **artifacts,
            "class_name": java_result.get("class_name"),
            "compiles": java_result.get("compiles", False),
            "java_status": java_result.get("status"),
            "normalized_compilation_unit_available": bool(java_result.get("normalized_compilation_unit")),
            "repair_metadata": java_result.get("repair_metadata", {}),
            "tree_sitter_available": java_result.get("tree_sitter_available", False),
            "tree_sitter_error": java_result.get("tree_sitter_error"),
        }

    def _build_semantic_artifacts(
        self,
        py_result: Dict[str, Any],
        java_result: Dict[str, Any],
        csr_score: float,
        candidate_metadata: Dict[str, Any],
        trusted_tests: Dict[str, Any],
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        python_ast = self._build_python_ast_artifact(py_result)
        java_parse_tree = self._build_java_parse_tree_artifact(java_result)
        return {
            "python_ast": python_ast,
            "java_parse_tree": java_parse_tree,
            "csr": {
                "csr_score": csr_score,
                "note": "CSR score only is stored; CSR token bags are recomputed when needed.",
            },
            "alignment": {
                "strategy": candidate_metadata.get("alignment_strategy", "unknown"),
                "confidence": candidate_metadata.get("alignment_confidence", 0.0),
                "python_ast_metadata_from_alignment": candidate_metadata.get("python_ast_metadata", {}),
                "java_structural_metadata_from_alignment": candidate_metadata.get("java_structural_metadata", {}),
            },
            "trusted_tests": {
                "status": trusted_tests.get("status") if isinstance(trusted_tests, dict) else None,
                "num_tests": len(trusted_tests.get("tests", [])) if isinstance(trusted_tests, dict) else 0,
                "num_candidate_tests": len(trusted_tests.get("candidate_tests", [])) if isinstance(trusted_tests, dict) else 0,
            },
            "execution": execution_result,
        }

    def _reject(
        self,
        row: CandidateRow,
        reason: str,
        details: Dict[str, Any],
        diagnostics: Dict[str, Any],
    ) -> RejectedRow:
        return RejectedRow(
            corpus_id=row.corpus_id,
            dataset=row.dataset,
            split=row.split,
            reason=reason,
            details=details,
            metadata=row.metadata,
            provenance=row.provenance,
            validation_diagnostics=dict(diagnostics),
        )

    # --------------------------------------------------------
    # Single-row validation
    # --------------------------------------------------------

    def validate_row(self, row: CandidateRow) -> Tuple[Optional[ApprovedRow], Optional[RejectedRow], Dict[str, Any]]:
        current = row
        repair_history: List[Dict[str, Any]] = []
        diagnostics: Dict[str, Any] = {}
        max_attempts = self.config.validation.max_repair_attempts_per_component
        repair_allowed = bool(getattr(self.config.validation, "enable_teacher_repair", False))
        if repair_allowed and self.repair_engine is None:
            self.repair_engine = RepairEngine(self.config)

        # Natural Language
        nl_result = self.validate_natural_language(current)
        if repair_allowed and nl_result["status"] != "PASS" and self.config.validation.enable_nl_repair:
            for attempt in range(1, max_attempts + 1):
                if nl_result["status"] == "PASS":
                    break
                current, history = self.repair_engine.repair_natural_language(
                    current,
                    nl_result.get("reason", "nl_validation_failed"),
                    attempt_number=attempt,
                )
                repair_history.append(history)
                nl_result = self.validate_natural_language(current)
        diagnostics["nl"] = nl_result
        if nl_result["status"] != "PASS":
            rejected = self._reject(current, "nl_validation_failed", nl_result, diagnostics)
            return None, rejected, {"status": "REJECTED", "reason": rejected.reason, "diagnostics": diagnostics}

        # Python
        py_result = self.python_validator.validate(current.python_code)
        if repair_allowed and py_result["status"] != "PASS" and self.config.validation.enable_python_repair:
            for attempt in range(1, max_attempts + 1):
                if py_result["status"] == "PASS":
                    break
                current, history = self.repair_engine.repair_python(
                    current,
                    py_result.get("reason", "python_validation_failed"),
                    attempt_number=attempt,
                )
                repair_history.append(history)
                py_result = self.python_validator.validate(current.python_code)
        diagnostics["python"] = py_result
        if py_result["status"] != "PASS":
            rejected = self._reject(current, "python_validation_failed", py_result, diagnostics)
            return None, rejected, {"status": "REJECTED", "reason": rejected.reason, "diagnostics": diagnostics}

        # Java
        java_result = self.java_validator.validate(current.java_code)
        if repair_allowed and java_result["status"] != "PASS" and self.config.validation.enable_java_wrapper_repair:
            for attempt in range(1, max_attempts + 1):
                if java_result["status"] == "PASS":
                    break
                current, history = self.repair_engine.repair_java_wrapper(
                    current,
                    java_result.get("reason", "java_validation_failed"),
                    attempt_number=attempt,
                )
                repair_history.append(history)
                java_result = self.java_validator.validate(current.java_code)
        diagnostics["java"] = java_result
        if java_result["status"] != "PASS":
            rejected = self._reject(current, "java_validation_failed", java_result, diagnostics)
            return None, rejected, {"status": "REJECTED", "reason": rejected.reason, "diagnostics": diagnostics}

        # Trusted tests and execution
        trusted_tests = self.test_builder.build(current)
        diagnostics["trusted_tests"] = trusted_tests
        execution_result = self.validate_execution(current, trusted_tests)
        diagnostics["execution"] = execution_result
        if execution_result["status"] == "FAIL" or (
            execution_result["status"] == "NOT_FEASIBLE" and not self.config.validation.allow_execution_not_feasible
        ):
            rejected = self._reject(current, "execution_validation_failed", execution_result, diagnostics)
            return None, rejected, {"status": "REJECTED", "reason": rejected.reason, "diagnostics": diagnostics}

        # CSR score only
        csr_python = self.csr_builder.build_python(current.python_code)
        csr_java = self.csr_builder.build_java(current.java_code)
        csr_score = self.csr_builder.similarity(csr_python, csr_java)
        diagnostics["csr_score"] = csr_score

        python_ast = self._build_python_ast_artifact(py_result)
        java_parse_tree = self._build_java_parse_tree_artifact(java_result)
        semantic_artifacts = self._build_semantic_artifacts(
            py_result=py_result,
            java_result=java_result,
            csr_score=csr_score,
            candidate_metadata=current.metadata,
            trusted_tests=trusted_tests,
            execution_result=execution_result,
        )

        approved = ApprovedRow(
            corpus_id=current.corpus_id,
            natural_language=current.natural_language or "",
            python_code=current.python_code,
            java_code=current.java_code,
            trusted_tests=trusted_tests,
            python_ast=python_ast,
            java_parse_tree=java_parse_tree,
            csr_score=csr_score,
            validation_status="APPROVED",
            repair_history=repair_history,
            corpus_version=self.config.corpus.corpus_version,
            metadata={
                **current.metadata,
                "csr_score": csr_score,
                "csr_above_threshold": csr_score >= self.config.validation.min_csr_similarity,
                "execution_status": execution_result.get("status"),
                "tree_sitter_java": self.java_validator.tree_sitter_available(),
                "java_structural_backend": java_parse_tree.get("backend"),
            },
            provenance=current.provenance,
            semantic_artifacts=semantic_artifacts,
        )

        report = {
            "corpus_id": current.corpus_id,
            "status": "APPROVED",
            "nl": nl_result,
            "python": py_result,
            "java": java_result,
            "trusted_tests": trusted_tests,
            "execution": execution_result,
            "csr_score": csr_score,
            "csr_above_threshold": csr_score >= self.config.validation.min_csr_similarity,
            "repair_history": repair_history,
            "semantic_artifacts": semantic_artifacts,
        }
        return approved, None, report

    # --------------------------------------------------------
    # Full-corpus validation
    # --------------------------------------------------------

    def run(self, candidate_rows: List[CandidateRow]):
        SectionPrinter.header("Corpus Validation Engine  [v2.4]")

        approved_rows: List[ApprovedRow] = []
        rejected_rows: List[RejectedRow] = []
        reports: List[Dict[str, Any]] = []
        trusted_test_repository_rows: List[Dict[str, Any]] = []
        csr_below_threshold = 0
        execution_not_feasible = 0

        for idx, row in enumerate(candidate_rows):
            approved, rejected, report = self.validate_row(row)
            reports.append(report)
            if approved is not None:
                approved_rows.append(approved)
                if not approved.metadata.get("csr_above_threshold", True):
                    csr_below_threshold += 1
                if approved.metadata.get("execution_status") == "NOT_FEASIBLE":
                    execution_not_feasible += 1
                trusted_test_repository_rows.append({
                    "corpus_id": approved.corpus_id,
                    "trusted_test_status": approved.trusted_tests.get("status"),
                    "num_trusted_tests": len(approved.trusted_tests.get("tests", [])),
                    "num_candidate_tests": len(approved.trusted_tests.get("candidate_tests", [])),
                    "sources": approved.trusted_tests.get("sources", []),
                    "notes": approved.trusted_tests.get("notes", ""),
                })
            if rejected is not None:
                rejected_rows.append(rejected)
            if (idx + 1) % 100 == 0:
                LOG.info(f"Validated {idx + 1}/{len(candidate_rows)} rows")

        self.storage.save_jsonl([dataclass_to_dict(row) for row in approved_rows], self.storage.approved_corpus_path())
        self.storage.save_jsonl([dataclass_to_dict(row) for row in rejected_rows], self.storage.rejected_corpus_path())
        self.storage.save_jsonl(reports, f"{self.config.storage.reports_dir}/validation_report.jsonl")
        self.storage.save_jsonl(
            trusted_test_repository_rows,
            f"{self.config.storage.trusted_tests_dir}/trusted_tests.jsonl",
        )

        SummaryPrinter.print_summary(
            "Corpus Validation Summary  [v2.4]",
            {
                "Candidate Rows": len(candidate_rows),
                "Approved Rows": len(approved_rows),
                "Rejected Rows": len(rejected_rows),
                "Approval Rate": round(len(approved_rows) / max(1, len(candidate_rows)), 4),
                "CSR Below Threshold (approved, recorded)": csr_below_threshold,
                "Execution NOT_FEASIBLE": execution_not_feasible,
                "Trusted Test Repository Rows": len(trusted_test_repository_rows),
                "Tree-sitter Java": self.java_validator.tree_sitter_available(),
            },
        )
        return approved_rows, rejected_rows, reports
