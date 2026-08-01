"""
============================================================
RepoCoder Studio
corpus_builder.py  —  v2
============================================================

Candidate Corpus Builder.

v2.1 changes
------------
- Semantic alignment: three independent pools (NL, Python, Java)
  are embedded and aligned via cosine similarity — no split-index
  or title-key correspondence assumed.
- align_xlcost() builds a deduplicated NL pool from both Python and
  Java configs, then calls the unified align() method.
- align_codexglue() uses the same align() method for cross-dataset
  embedding alignment (Python and Java configs are independent).
- Stores alignment evidence (confidence, strategy) in CandidateRow
  metadata so it is available downstream.

Design boundary
---------------
This module builds CandidateRow objects.
It does not validate code correctness.
It does not repair code.
"""

from typing import Any, Dict, List, Optional

from src.config import CONFIG, AppConfig
from src.schemas import CandidateRow, dataclass_to_dict
from src.storage import ProjectStorageManager
from src.duplicate_detector import DuplicateDetector
from src.normalization_engine import NORMALIZER_VERSION, NormalizationEngine
from src.semantic_alignment_engine import SemanticAlignmentEngine
from src.utils import stable_id, normalize_whitespace
from src.logger import LOG, SectionPrinter, SummaryPrinter


class CandidateCorpusBuilder:
    """
    Builds CandidateRow objects from raw dataset bundles.

    v2 flow
    -------
    1. Normalize raw XLCoST records (detokenize NEW_LINE, INDENT etc.)
    2. Pass normalized Python and Java splits to SemanticAlignmentEngine.
    3. Convert each AlignmentRecord into a CandidateRow.
    4. For CodeXGLUE: normalize, call align_codexglue(), convert to CandidateRow.
    5. Deduplicate across all datasets.
    """

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.normalizer = NormalizationEngine()
        self.alignment_engine = SemanticAlignmentEngine(config)

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    def _first_present(self, row: Dict[str, Any], keys: List[str], default=None):
        for key in keys:
            if key in row and row[key] is not None:
                value = row[key]
                if isinstance(value, str) and not value.strip():
                    continue
                return value
        return default

    def _sample_split(self, dataset_split, split: str, limit: Optional[int]):
        """Return a reproducible, non-prefix-biased subset of a HF split.

        The same split-specific seed is deliberately used for the Python and
        Java XLCoST configurations. If their source rows are parallel this
        preserves the pairing; if they are not, the semantic aligner remains
        the authority. This avoids the topic/order bias caused by always
        taking ``range(limit)`` in small demo and capstone profiles.
        """
        if limit is None or len(dataset_split) <= limit:
            return dataset_split
        split_offsets = {"train": 0, "validation": 1, "valid": 1, "dev": 1, "test": 2}
        seed = int(self.config.runtime.random_seed) + split_offsets.get(split, 3)
        return dataset_split.shuffle(seed=seed).select(range(int(limit)))

    def _normalize_nl(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, list):
            value = " ".join(str(x) for x in value)
        value = normalize_whitespace(str(value))
        return value if value else None

    # --------------------------------------------------------
    # XLCoST row normalization (pre-alignment)
    # --------------------------------------------------------

    def _normalize_xlcost_split(
        self,
        dataset_split,
        language: str,
    ) -> List[Dict[str, Any]]:
        """
        Normalizes one XLCoST split (e.g. Python-train) into dicts
        that the SemanticAlignmentEngine can consume.

        Each dict has:
          natural_language, python_code|java_code, _record_id
        """
        rows = []
        for idx, raw in enumerate(dataset_split):
            raw = dict(raw)

            nl = self._normalize_nl(
                self._first_present(
                    raw,
                    ["text", "docstring", "nl", "description", "problem",
                     "intent", "title", "question"],
                )
            )

            code_raw = self._first_present(
                raw,
                ["code", "program", "source", "solution", "function", "snippet"],
            )
            code_raw = "" if code_raw is None else str(code_raw)

            if language == "python":
                code = self.normalizer.normalize_python(code_raw)
                row = {
                    "natural_language": nl,
                    "python_code": code,
                    "text": nl,
                    "code": code,
                    "_record_id": str(idx),
                }
            elif language == "java":
                code = self.normalizer.normalize_java(code_raw)
                row = {
                    "natural_language": nl,
                    "java_code": code,
                    "text": nl,
                    "code": code,
                    "_record_id": str(idx),
                }
            else:
                continue

            rows.append(row)

        return rows

    # --------------------------------------------------------
    # CodeXGLUE row normalization (pre-alignment)
    # --------------------------------------------------------

    def _normalize_codexglue_split(
        self,
        dataset_split,
        language: str,
    ) -> List[Dict[str, Any]]:
        """
        Normalizes one CodeXGLUE (code_search_net) split into dicts
        consumable by SemanticAlignmentEngine.

        CodeXGLUE field mapping:
          func_documentation_string  →  natural_language
          func_code_string           →  python_code / java_code
          docstring                  →  fallback NL
          code                       →  fallback code
        """
        rows = []
        for idx, raw in enumerate(dataset_split):
            raw = dict(raw)

            nl = self._normalize_nl(
                self._first_present(
                    raw,
                    ["func_documentation_string", "docstring", "text", "nl"],
                )
            )

            code_raw = self._first_present(
                raw,
                ["func_code_string", "code", "function"],
            )
            code_raw = "" if code_raw is None else str(code_raw)

            if language == "python":
                code = self.normalizer.normalize_python(code_raw)
                row = {
                    "natural_language": nl,
                    "python_code": code,
                    "text": nl,
                    "code": code,
                    "_record_id": f"csn_py_{idx}",
                }
            elif language == "java":
                code = self.normalizer.normalize_java(code_raw)
                row = {
                    "natural_language": nl,
                    "java_code": code,
                    "text": nl,
                    "code": code,
                    "_record_id": f"csn_java_{idx}",
                }
            else:
                continue

            if nl and code:
                rows.append(row)

        return rows

    # --------------------------------------------------------
    # XLCoST corpus construction (v2: semantic alignment)
    # --------------------------------------------------------

    def build_xlcost_rows(self, xlcost_bundle: Dict[str, Any]) -> List[CandidateRow]:
        SectionPrinter.header("Building XLCoST Candidate Rows (Semantic Alignment)")

        python_ds = xlcost_bundle["python"]
        java_ds = xlcost_bundle["java"]

        common_splits = sorted(set(python_ds.keys()) & set(java_ds.keys()))
        assert common_splits, "No common XLCoST splits found."

        py_splits_normalized: Dict[str, List[Dict]] = {}
        java_splits_normalized: Dict[str, List[Dict]] = {}

        for split in common_splits:
            limit = self.config.dataset.get_split_limit(split, self.config.runtime.run_mode)
            py_raw = python_ds[split]
            java_raw = java_ds[split]
            py_raw = self._sample_split(py_raw, split, limit)
            java_raw = self._sample_split(java_raw, split, limit)

            py_splits_normalized[split] = self._normalize_xlcost_split(py_raw, "python")
            java_splits_normalized[split] = self._normalize_xlcost_split(java_raw, "java")

        aligned_dicts = self.alignment_engine.align_xlcost(
            py_splits_normalized,
            java_splits_normalized,
        )

        candidate_rows: List[CandidateRow] = []

        for aligned in aligned_dicts:
            python_code = aligned["python_code"]
            java_code = aligned["java_code"]
            nl = aligned["natural_language"]

            if len(python_code.strip()) < self.config.corpus.min_python_chars:
                continue
            if len(java_code.strip()) < self.config.corpus.min_java_chars:
                continue
            if nl and len(nl.split()) < self.config.corpus.min_nl_words:
                nl = None

            corpus_id = stable_id(
                "xlcost",
                aligned["split"],
                aligned.get("alignment_id", ""),
                python_code,
                java_code,
            )

            candidate_rows.append(
                CandidateRow(
                    corpus_id=corpus_id,
                    dataset="XLCoST",
                    dataset_record_id=aligned.get("alignment_id", corpus_id),
                    split=aligned["split"],
                    natural_language=nl,
                    python_code=python_code,
                    java_code=java_code,
                    metadata={
                        "alignment_strategy": aligned.get("alignment_strategy", "semantic_embedding"),
                        "alignment_confidence": aligned.get("confidence", 1.0),
                        "python_ast_metadata": aligned.get("python_ast_metadata", {}),
                        "java_structural_metadata": aligned.get("java_structural_metadata", {}),
                        "normalized": True,
                        "normalizer_version": NORMALIZER_VERSION,
                    },
                    provenance={
                        "dataset": self.config.dataset.xlcost_dataset_name,
                        "python_config": self.config.dataset.xlcost_python_config,
                        "java_config": self.config.dataset.xlcost_java_config,
                        "split": aligned["split"],
                        "alignment_provenance": aligned.get("provenance", {}),
                        "adapter_version": "xlcost_adapter_v2.0_semantic",
                        "corpus_version": self.config.corpus.corpus_version,
                    },
                )
            )

        SummaryPrinter.print_summary(
            "XLCoST Candidate Row Summary",
            {
                "Aligned pairs": len(aligned_dicts),
                "Rows Created": len(candidate_rows),
                "Splits": common_splits,
            },
        )

        return candidate_rows

    # --------------------------------------------------------
    # CodeXGLUE corpus construction (v2: cross-dataset embedding)
    # --------------------------------------------------------

    def build_codexglue_rows(self, codexglue_bundle: Dict[str, Any]) -> List[CandidateRow]:
        """
        Builds CandidateRow objects from CodeXGLUE (code_search_net).

        CodeXGLUE Python and Java configs have no positional alignment,
        so Tier 2 cross-dataset embedding alignment is used exclusively.
        """
        SectionPrinter.header("Building CodeXGLUE Candidate Rows (Embedding Alignment)")

        python_ds = codexglue_bundle["python"]
        java_ds = codexglue_bundle["java"]

        common_splits = sorted(set(python_ds.keys()) & set(java_ds.keys()))
        if not common_splits:
            LOG.warning("No common CodeXGLUE splits found.")
            return []

        py_splits: Dict[str, List[Dict]] = {}
        java_splits: Dict[str, List[Dict]] = {}

        for split in common_splits:
            limit = self.config.dataset.get_split_limit(split, self.config.runtime.run_mode)
            py_raw = python_ds[split]
            java_raw = java_ds[split]
            py_raw = self._sample_split(py_raw, split, limit)
            java_raw = self._sample_split(java_raw, split, limit)

            py_splits[split] = self._normalize_codexglue_split(py_raw, "python")
            java_splits[split] = self._normalize_codexglue_split(java_raw, "java")

        aligned_dicts = self.alignment_engine.align_codexglue(py_splits, java_splits)

        candidate_rows: List[CandidateRow] = []

        for aligned in aligned_dicts:
            python_code = aligned["python_code"]
            java_code = aligned["java_code"]
            nl = aligned["natural_language"]

            if len(python_code.strip()) < self.config.corpus.min_python_chars:
                continue
            if len(java_code.strip()) < self.config.corpus.min_java_chars:
                continue
            if nl and len(nl.split()) < self.config.corpus.min_nl_words:
                nl = None

            corpus_id = stable_id(
                "codexglue",
                aligned["split"],
                aligned.get("alignment_id", ""),
                python_code,
                java_code,
            )

            candidate_rows.append(
                CandidateRow(
                    corpus_id=corpus_id,
                    dataset="CodeXGLUE",
                    dataset_record_id=aligned.get("alignment_id", corpus_id),
                    split=aligned["split"],
                    natural_language=nl,
                    python_code=python_code,
                    java_code=java_code,
                    metadata={
                        "alignment_strategy": aligned.get("alignment_strategy", "semantic_embedding"),
                        "alignment_confidence": aligned.get("confidence", 0.0),
                        "python_ast_metadata": aligned.get("python_ast_metadata", {}),
                        "java_structural_metadata": aligned.get("java_structural_metadata", {}),
                        "normalized": True,
                        "normalizer_version": NORMALIZER_VERSION,
                    },
                    provenance={
                        "dataset": self.config.dataset.codexglue_dataset_name,
                        "python_config": self.config.dataset.codexglue_python_config,
                        "java_config": self.config.dataset.codexglue_java_config,
                        "split": aligned["split"],
                        "alignment_provenance": aligned.get("provenance", {}),
                        "adapter_version": "codexglue_adapter_v2.0_embedding",
                        "corpus_version": self.config.corpus.corpus_version,
                    },
                )
            )

        SummaryPrinter.print_summary(
            "CodeXGLUE Candidate Row Summary",
            {
                "Aligned pairs": len(aligned_dicts),
                "Rows Created": len(candidate_rows),
                "Splits": common_splits,
            },
        )

        return candidate_rows

    # --------------------------------------------------------
    # AVATAR rows (unchanged — local JSONL, kept as fallback)
    # --------------------------------------------------------

    def build_avatar_rows(self, avatar_bundle: Optional[Dict[str, Any]]) -> List[CandidateRow]:
        if not avatar_bundle:
            LOG.info("No AVATAR bundle provided. Skipping AVATAR.")
            return []

        SectionPrinter.header("Building AVATAR Candidate Rows")

        rows = []

        for split, records in avatar_bundle.items():
            for idx, record in enumerate(records):
                natural_language = self._normalize_nl(
                    self._first_present(record, ["natural_language", "problem", "description", "text"])
                )
                python_code = str(self._first_present(record, ["python_code", "python", "py"], ""))
                java_code = str(self._first_present(record, ["java_code", "java"], ""))

                if not python_code.strip() or not java_code.strip():
                    continue

                corpus_id = stable_id("avatar", split, str(idx), python_code, java_code)

                rows.append(
                    CandidateRow(
                        corpus_id=corpus_id,
                        dataset="AVATAR",
                        dataset_record_id=str(idx),
                        split=split,
                        natural_language=natural_language,
                        python_code=python_code,
                        java_code=java_code,
                        metadata={"adapter": "avatar_local_jsonl"},
                        provenance={
                            "dataset": "AVATAR",
                            "source": self.config.dataset.avatar_local_dir,
                            "split": split,
                            "record_index": idx,
                            "adapter_version": "avatar_adapter_v1.0",
                            "corpus_version": self.config.corpus.corpus_version,
                        },
                    )
                )

        return rows

    # --------------------------------------------------------
    # Main builder
    # --------------------------------------------------------

    def build(self, raw_datasets: Dict[str, Any]) -> List[CandidateRow]:
        SectionPrinter.header("Candidate Corpus Builder  [v2 — Semantic Alignment]")

        rows: List[CandidateRow] = []

        assert "XLCoST" in raw_datasets, "XLCoST raw dataset missing."

        rows.extend(self.build_xlcost_rows(raw_datasets["XLCoST"]))

        if "CodeXGLUE" in raw_datasets:
            rows.extend(self.build_codexglue_rows(raw_datasets["CodeXGLUE"]))

        if "AVATAR" in raw_datasets:
            rows.extend(self.build_avatar_rows(raw_datasets["AVATAR"]))

        assert len(rows) > 0, "Candidate Corpus is empty after construction."

        duplicate_report = []

        if self.config.corpus.enable_deduplication:
            detector = DuplicateDetector(
                remove_exact=self.config.corpus.remove_exact_duplicates,
                remove_structural=self.config.corpus.remove_structural_duplicates,
            )
            rows, duplicate_report = detector.deduplicate(rows)

        self.storage.save_jsonl(
            [dataclass_to_dict(row) for row in rows],
            self.storage.candidate_corpus_path(),
        )

        self.storage.save_jsonl(
            duplicate_report,
            self.storage.duplicate_report_path(),
        )

        SummaryPrinter.print_summary(
            "Candidate Corpus Build Summary",
            {
                "Final Candidate Rows": len(rows),
                "Duplicates Removed": len(duplicate_report),
                "Saved Path": self.storage.candidate_corpus_path(),
            },
        )

        return rows
