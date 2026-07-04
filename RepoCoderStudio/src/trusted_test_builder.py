"""
============================================================
RepoCoder Studio
trusted_test_builder.py — v2.3 Batch 2
============================================================

Trusted Test Builder.

Design role
-----------
Builds the trusted-test bundle attached to each CandidateRow during corpus
validation. This module is intentionally conservative. Teacher-generated
tests are persisted as candidate tests but are not promoted to trusted tests
without a deterministic validator.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.config import CONFIG, AppConfig
from src.schemas import CandidateRow
from src.teacher_engine import TeacherEngine
from src.utils import stable_id


class TrustedTestBuilder:
    """Conservative trusted-test metadata builder."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.teacher = TeacherEngine(config)

    def _metadata_tests(self, row: CandidateRow) -> List[Dict[str, Any]]:
        metadata_tests = row.metadata.get("tests") if isinstance(row.metadata, dict) else None
        tests: List[Dict[str, Any]] = []
        if isinstance(metadata_tests, list):
            for idx, test in enumerate(metadata_tests[: self.config.validation.max_execution_tests_per_row]):
                if not isinstance(test, dict):
                    continue
                tests.append({
                    "test_id": stable_id("trusted_test", row.corpus_id, str(idx)),
                    "corpus_id": row.corpus_id,
                    "source": "dataset_metadata",
                    "status": "trusted",
                    "test": test,
                })
        return tests

    def _teacher_candidate_tests(self, row: CandidateRow) -> List[Dict[str, Any]]:
        if not bool(getattr(self.config.validation, "enable_teacher_test_generation", False)):
            return []

        proposed = self.teacher.propose_tests(
            natural_language=row.natural_language or "",
            python_code=row.python_code,
            java_code=row.java_code,
        )

        tests: List[Dict[str, Any]] = []
        for idx, test in enumerate(proposed.get("candidate_tests", [])[: self.config.validation.max_execution_tests_per_row]):
            tests.append({
                "test_id": stable_id("teacher_candidate_test", row.corpus_id, str(idx)),
                "corpus_id": row.corpus_id,
                "source": "teacher_candidate",
                "status": "untrusted_candidate",
                "test": test,
                "teacher_status": proposed.get("status"),
                "teacher_reason": proposed.get("reason"),
            })
        return tests

    def build(self, row: CandidateRow) -> Dict[str, Any]:
        trusted = self._metadata_tests(row)
        if trusted:
            return {
                "status": "trusted",
                "tests": trusted,
                "candidate_tests": [],
                "sources": sorted({t["source"] for t in trusted}),
                "notes": "Trusted tests extracted from metadata.",
            }

        candidates = self._teacher_candidate_tests(row)
        if candidates:
            return {
                "status": "insufficient",
                "tests": [],
                "candidate_tests": candidates,
                "sources": ["teacher_candidate"],
                "notes": "Teacher proposed candidate tests, but no deterministic validator promoted them to trusted tests.",
            }

        return {
            "status": "insufficient",
            "tests": [],
            "candidate_tests": [],
            "sources": [],
            "notes": "No trusted logical tests available.",
        }
