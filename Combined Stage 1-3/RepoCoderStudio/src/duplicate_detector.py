"""
============================================================
RepoCoder Studio
duplicate_detector.py
============================================================

Duplicate detection for Candidate Corpus construction.

Purpose
-------
Removes exact and structural duplicates before expensive
validation.

Stage Learning
--------------
Stage 3 showed that validation can be slow. Therefore, duplicate
removal must happen before validation, repair, and training.
"""

import re
from typing import Dict, List, Tuple

from src.schemas import CandidateRow
from src.utils import sha1_text
from src.logger import LOG, SectionPrinter, SummaryPrinter


class DuplicateDetector:
    """
    Detects and removes duplicate CandidateRow objects.

    Duplicate types
    ---------------
    exact:
        Same Python and Java code after whitespace removal.

    structural:
        Same approximate structure after removing identifiers,
        literals, comments, and whitespace.
    """

    def __init__(self, remove_exact: bool = True, remove_structural: bool = True):
        self.remove_exact = remove_exact
        self.remove_structural = remove_structural

    def _normalize_exact(self, text: str) -> str:
        """Removes whitespace for exact duplicate comparison."""
        return re.sub(r"\s+", "", text or "")

    def _normalize_structural(self, text: str) -> str:
        """
        Produces a lightweight structural normalization.

        This is not semantic equivalence.
        It is only used to avoid obvious repeated rows.
        """

        text = text or ""

        # Remove common comment forms.
        text = re.sub(r"#.*", "", text)
        text = re.sub(r"//.*", "", text)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)

        # Replace identifiers and numbers.
        text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", "ID", text)
        text = re.sub(r"\d+(\.\d+)?", "NUM", text)

        # Remove whitespace.
        text = re.sub(r"\s+", "", text)

        return text

    def exact_key(self, row: CandidateRow) -> str:
        """Creates exact duplicate key for Python-Java pair."""
        combined = (
            self._normalize_exact(row.python_code)
            + "::"
            + self._normalize_exact(row.java_code)
        )
        return sha1_text(combined)

    def structural_key(self, row: CandidateRow) -> str:
        """Creates approximate structural duplicate key."""
        combined = (
            self._normalize_structural(row.python_code)
            + "::"
            + self._normalize_structural(row.java_code)
        )
        return sha1_text(combined)

    def deduplicate(
        self,
        rows: List[CandidateRow],
    ) -> Tuple[List[CandidateRow], List[Dict]]:
        """
        Removes duplicates from Candidate Corpus.

        Returns
        -------
        kept_rows:
            Deduplicated candidate rows.

        duplicate_report:
            Rows removed with duplicate reason.
        """

        SectionPrinter.header("Duplicate Detection")

        seen_exact = {}
        seen_structural = {}

        kept_rows = []
        duplicate_report = []

        for row in rows:
            exact_key = self.exact_key(row)
            structural_key = self.structural_key(row)

            if self.remove_exact and exact_key in seen_exact:
                duplicate_report.append({
                    "corpus_id": row.corpus_id,
                    "duplicate_of": seen_exact[exact_key],
                    "duplicate_type": "exact",
                    "action": "removed",
                    "dataset": row.dataset,
                    "split": row.split,
                })
                continue

            if self.remove_structural and structural_key in seen_structural:
                duplicate_report.append({
                    "corpus_id": row.corpus_id,
                    "duplicate_of": seen_structural[structural_key],
                    "duplicate_type": "structural",
                    "action": "removed",
                    "dataset": row.dataset,
                    "split": row.split,
                })
                continue

            seen_exact[exact_key] = row.corpus_id
            seen_structural[structural_key] = row.corpus_id
            kept_rows.append(row)

        SummaryPrinter.print_summary(
            "Duplicate Detection Summary",
            {
                "Input Rows": len(rows),
                "Kept Rows": len(kept_rows),
                "Duplicates Removed": len(duplicate_report),
            },
        )

        return kept_rows, duplicate_report
