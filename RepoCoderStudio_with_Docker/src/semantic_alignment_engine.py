"""
============================================================
RepoCoder Studio
semantic_alignment_engine.py  —  v2.2 Batch 1
============================================================

Semantic Alignment Engine for RepoCoder Studio v2.

Design role
-----------
This module constructs candidate NL-Python-Java alignments from
validated or normalized evidence pools. It does not approve rows,
train models, or evaluate predictions.

Batch 1 improvements
--------------------
1. Robust Tree-sitter Java initialization for modern and older APIs.
2. XLCoST semantic alignment retains the v2 evidence-pool approach.
3. CodeXGLUE alignment uses docstring semantics explicitly.
4. Unmatched CodeXGLUE evidence is persisted as a teacher-completion queue.
5. Alignment analytics are retained on the engine instance and can be printed
   or saved by notebook blocks.
6. Java structural metadata records the parsing backend clearly.

Important policy
----------------
CodeXGLUE is not guaranteed to contain paired Python and Java solutions.
Therefore, weak Python-Java matches are not forced into the Candidate Corpus.
High-confidence docstring matches become CandidateRows. Unmatched evidence is
stored for later Teacher Completion rather than being silently discarded.
"""

from __future__ import annotations

import ast
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.config import CONFIG, AppConfig
from src.schemas import AlignmentRecord
from src.storage import ProjectStorageManager
from src.logger import LOG, SectionPrinter, SummaryPrinter
from src.utils import stable_id


# ============================================================
# Robust Tree-sitter Java initialization
# ============================================================

_TS_AVAILABLE = False
_TS_PARSER = None
_TS_INIT_ERROR: Optional[str] = None


def _init_tree_sitter_java() -> None:
    """
    Initializes Tree-sitter Java parser.

    Supports both common Tree-sitter APIs:
    - Parser(Language(...))
    - Parser(); parser.set_language(Language(...))

    Failure is non-fatal because semantic alignment can still proceed using
    embeddings and lightweight metadata. The backend is recorded explicitly.
    """
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


# ============================================================
# Helper functions
# ============================================================


def _normalize_description(text: str) -> str:
    """Returns a stable normalized text key for exact/fallback matching."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize_words(text: str) -> set:
    return set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", (text or "").lower()))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _cosine_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Normalized cosine similarity matrix."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a_norm @ b_norm.T


def _python_ast_metadata(python_code: str) -> Dict[str, Any]:
    """Extracts parser-derived Python structural metadata with stdlib ast."""
    meta: Dict[str, Any] = {
        "backend": "ast",
        "parse_ok": False,
        "function_count": 0,
        "class_count": 0,
        "import_count": 0,
        "function_names": [],
        "class_names": [],
        "has_loop": False,
        "has_conditional": False,
        "has_recursion": False,
        "ast_node_count": 0,
    }

    if not python_code or not python_code.strip():
        meta["reason"] = "empty_python_code"
        return meta

    try:
        tree = ast.parse(python_code)
    except Exception as exc:
        meta["reason"] = repr(exc)
        return meta

    meta["parse_ok"] = True
    function_names: List[str] = []
    class_names: List[str] = []
    call_names: set = set()

    for node in ast.walk(tree):
        meta["ast_node_count"] += 1
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            class_names.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            meta["import_count"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            meta["has_loop"] = True
        elif isinstance(node, ast.If):
            meta["has_conditional"] = True
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)

    meta["function_names"] = function_names
    meta["class_names"] = class_names
    meta["function_count"] = len(function_names)
    meta["class_count"] = len(class_names)
    meta["has_recursion"] = bool(set(function_names) & call_names)
    return meta


def _walk_ts(node):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def _java_structural_metadata_tree_sitter(java_code: str) -> Dict[str, Any]:
    """Extracts Java structural metadata using Tree-sitter."""
    meta: Dict[str, Any] = {
        "backend": "tree_sitter",
        "parse_ok": False,
        "method_count": 0,
        "class_count": 0,
        "method_names": [],
        "class_names": [],
        "has_loop": False,
        "has_conditional": False,
        "parse_tree_node_count": 0,
    }

    if not _TS_AVAILABLE or _TS_PARSER is None:
        meta["backend"] = "tree_sitter_unavailable"
        meta["reason"] = _TS_INIT_ERROR
        return meta

    try:
        src = java_code.encode("utf-8", errors="replace")
        tree = _TS_PARSER.parse(src)
        meta["parse_ok"] = not bool(getattr(tree.root_node, "has_error", False))

        method_names: List[str] = []
        class_names: List[str] = []

        for node in _walk_ts(tree.root_node):
            meta["parse_tree_node_count"] += 1
            node_type = node.type

            if node_type == "class_declaration":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    class_names.append(src[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace"))
            elif node_type in {"method_declaration", "constructor_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    method_names.append(src[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace"))
            elif node_type in {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}:
                meta["has_loop"] = True
            elif node_type == "if_statement":
                meta["has_conditional"] = True

        meta["method_names"] = method_names
        meta["class_names"] = class_names
        meta["method_count"] = len(method_names)
        meta["class_count"] = len(class_names)
        return meta

    except Exception as exc:
        meta["backend"] = "tree_sitter_error"
        meta["reason"] = repr(exc)
        return meta


def _java_structural_metadata_regex_fallback(java_code: str) -> Dict[str, Any]:
    """Fallback metadata only. This is explicitly marked as non-parser backend."""
    class_names = re.findall(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", java_code or "")
    method_like = re.findall(
        r"\b(?:public|private|protected|static|final|void|int|long|double|float|boolean|String|List|Map|Set)\b[^;{}]*\(",
        java_code or "",
    )
    return {
        "backend": "regex_fallback",
        "parse_ok": False,
        "method_count": len(method_like),
        "class_count": len(class_names),
        "method_names": [],
        "class_names": class_names,
        "has_loop": bool(re.search(r"\b(for|while)\s*\(", java_code or "")),
        "has_conditional": bool(re.search(r"\bif\s*\(", java_code or "")),
        "tree_sitter_error": _TS_INIT_ERROR,
    }


def _java_structural_metadata(java_code: str) -> Dict[str, Any]:
    if not java_code or not java_code.strip():
        return {
            "backend": "empty",
            "parse_ok": False,
            "method_count": 0,
            "class_count": 0,
            "method_names": [],
            "class_names": [],
            "has_loop": False,
            "has_conditional": False,
        }

    if _TS_AVAILABLE and _TS_PARSER is not None:
        return _java_structural_metadata_tree_sitter(java_code)

    return _java_structural_metadata_regex_fallback(java_code)


def _structural_compatibility(py_meta: Dict[str, Any], java_meta: Dict[str, Any], max_bonus: float = 0.10) -> float:
    """Small bounded structural bonus used only as alignment support."""
    py_count = max(1, int(py_meta.get("function_count", 0) or 0))
    java_count = max(1, int(java_meta.get("method_count", 0) or 0))
    ratio = min(py_count, java_count) / max(py_count, java_count)

    control_bonus = 0.0
    if bool(py_meta.get("has_loop")) == bool(java_meta.get("has_loop")):
        control_bonus += 0.02
    if bool(py_meta.get("has_conditional")) == bool(java_meta.get("has_conditional")):
        control_bonus += 0.02

    return min(max_bonus, (max_bonus * 0.60 * ratio) + control_bonus)


class SemanticAlignmentEngine:
    """Builds candidate semantic alignments from evidence pools."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self._embedding_model = None
        self.last_alignment_analytics: List[Dict[str, Any]] = []
        self.teacher_completion_queue: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    def _load_embedding_model(self):
        if self._embedding_model is not None:
            return self._embedding_model

        try:
            from sentence_transformers import SentenceTransformer

            LOG.info(f"Loading sentence-transformer: {self.config.alignment.embedding_model}")
            self._embedding_model = SentenceTransformer(self.config.alignment.embedding_model)
            return self._embedding_model
        except Exception as exc:
            LOG.warning(f"SentenceTransformer unavailable. Semantic alignment fallback will be used. Error: {exc}")
            self._embedding_model = None
            return None

    def _embed(self, texts: List[str]) -> Optional[np.ndarray]:
        model = self._load_embedding_model()
        if model is None:
            return None
        if not texts:
            return np.empty((0, 0))
        return np.asarray(
            model.encode(texts, normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float32,
        )

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def _record_to_dict(self, record: AlignmentRecord) -> Dict[str, Any]:
        return {
            "alignment_id": record.alignment_id,
            "natural_language": record.natural_language,
            "python_code": record.python_code,
            "java_code": record.java_code,
            "confidence": record.confidence,
            "alignment_strategy": record.alignment_strategy,
            "python_ast_metadata": record.python_ast_metadata,
            "java_structural_metadata": record.java_structural_metadata,
            "provenance": record.provenance,
            "split": record.split,
        }

    def _save_teacher_queue(self) -> None:
        if not self.teacher_completion_queue:
            return
        self.storage.save_jsonl(
            self.teacher_completion_queue,
            "outputs/teacher_queue/teacher_completion_queue.jsonl",
        )

    def _save_alignment_analytics(self) -> None:
        if not self.last_alignment_analytics:
            return
        self.storage.save_jsonl(
            self.last_alignment_analytics,
            "outputs/reports/alignment_analytics.jsonl",
        )

    # --------------------------------------------------------
    # Generic three-pool alignment
    # --------------------------------------------------------

    def align(
        self,
        nl_records: List[Dict[str, Any]],
        python_records: List[Dict[str, Any]],
        java_records: List[Dict[str, Any]],
        split: str,
        dataset_label: str = "generic",
        strategy: str = "semantic_embedding",
    ) -> List[AlignmentRecord]:
        """Aligns NL, Python and Java evidence pools using embeddings."""
        threshold = self.config.alignment.confidence_threshold
        top_k = max(1, int(self.config.alignment.alignment_top_k))

        clean_nl = [r for r in nl_records if (r.get("natural_language") or "").strip()]
        clean_py = [r for r in python_records if (r.get("python_code") or r.get("code") or "").strip()]
        clean_java = [r for r in java_records if (r.get("java_code") or r.get("code") or "").strip()]

        if not clean_nl or not clean_py or not clean_java:
            self.last_alignment_analytics.append({
                "dataset": dataset_label,
                "split": split,
                "strategy": strategy,
                "nl_records": len(clean_nl),
                "python_records": len(clean_py),
                "java_records": len(clean_java),
                "accepted": 0,
                "below_threshold": 0,
                "tree_sitter_available": _TS_AVAILABLE,
                "note": "empty_pool",
            })
            return []

        nl_texts = [(r.get("natural_language") or "").strip() for r in clean_nl]
        py_texts = [(r.get("natural_language") or r.get("text") or "").strip() for r in clean_py]
        java_texts = [(r.get("natural_language") or r.get("text") or "").strip() for r in clean_java]

        nl_emb = self._embed(nl_texts)
        py_emb = self._embed(py_texts)
        java_emb = self._embed(java_texts)

        if nl_emb is None or py_emb is None or java_emb is None:
            return self._exact_nl_fallback(clean_nl, clean_py, clean_java, split, dataset_label)

        nl_py_sim = _cosine_matrix(nl_emb, py_emb)
        nl_java_sim = _cosine_matrix(nl_emb, java_emb)

        records: List[AlignmentRecord] = []
        seen_ids: set = set()
        below_threshold = 0
        examined = 0
        accepted_scores: List[float] = []

        for i, nl_rec in enumerate(clean_nl):
            nl = (nl_rec.get("natural_language") or "").strip()
            if not nl:
                continue

            py_candidates = np.argsort(-nl_py_sim[i])[:top_k]
            java_candidates = np.argsort(-nl_java_sim[i])[:top_k]

            best: Optional[Tuple[Any, ...]] = None
            best_confidence = -1.0

            for py_idx in py_candidates:
                py_sim = float(nl_py_sim[i, py_idx])
                if py_sim < threshold:
                    continue

                py_rec = clean_py[int(py_idx)]
                python_code = (py_rec.get("python_code") or py_rec.get("code") or "").strip()
                if not python_code:
                    continue

                py_meta = _python_ast_metadata(python_code)

                for java_idx in java_candidates:
                    examined += 1
                    java_sim = float(nl_java_sim[i, java_idx])
                    if java_sim < threshold:
                        continue

                    java_rec = clean_java[int(java_idx)]
                    java_code = (java_rec.get("java_code") or java_rec.get("code") or "").strip()
                    if not java_code:
                        continue

                    java_meta = _java_structural_metadata(java_code)
                    struct_bonus = _structural_compatibility(py_meta, java_meta, self.config.alignment.structural_bonus)
                    confidence = min(1.0, ((py_sim + java_sim) / 2.0) + struct_bonus)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best = (
                            int(py_idx), int(java_idx), py_sim, java_sim, struct_bonus,
                            confidence, py_meta, java_meta, python_code, java_code, py_rec, java_rec,
                        )

            if best is None or best_confidence < threshold:
                below_threshold += 1
                continue

            (
                py_idx, java_idx, py_sim, java_sim, struct_bonus, confidence,
                py_meta, java_meta, python_code, java_code, py_rec, java_rec,
            ) = best

            aid = stable_id(dataset_label, split, nl[:120], python_code[:120], java_code[:120])
            if aid in seen_ids:
                continue
            seen_ids.add(aid)

            records.append(
                AlignmentRecord(
                    alignment_id=aid,
                    natural_language=nl,
                    python_code=python_code,
                    java_code=java_code,
                    confidence=confidence,
                    alignment_strategy=strategy,
                    python_ast_metadata=py_meta,
                    java_structural_metadata=java_meta,
                    provenance={
                        "dataset": dataset_label,
                        "split": split,
                        "nl_record_id": nl_rec.get("_record_id", ""),
                        "py_record_id": py_rec.get("_record_id", ""),
                        "java_record_id": java_rec.get("_record_id", ""),
                        "nl_py_similarity": round(py_sim, 4),
                        "nl_java_similarity": round(java_sim, 4),
                        "structural_bonus": round(struct_bonus, 4),
                        "python_candidate_rank": int(np.where(py_candidates == py_idx)[0][0]) if py_idx in py_candidates else None,
                        "java_candidate_rank": int(np.where(java_candidates == java_idx)[0][0]) if java_idx in java_candidates else None,
                    },
                    split=split,
                )
            )
            accepted_scores.append(confidence)

        self.last_alignment_analytics.append({
            "dataset": dataset_label,
            "split": split,
            "strategy": strategy,
            "nl_records": len(clean_nl),
            "python_records": len(clean_py),
            "java_records": len(clean_java),
            "candidate_pairs_examined": examined,
            "accepted": len(records),
            "below_threshold_or_unmatched": below_threshold,
            "threshold": threshold,
            "mean_accepted_confidence": float(np.mean(accepted_scores)) if accepted_scores else 0.0,
            "min_accepted_confidence": float(np.min(accepted_scores)) if accepted_scores else 0.0,
            "max_accepted_confidence": float(np.max(accepted_scores)) if accepted_scores else 0.0,
            "tree_sitter_available": _TS_AVAILABLE,
            "tree_sitter_error": _TS_INIT_ERROR,
        })

        return records

    def _exact_nl_fallback(
        self,
        nl_records: List[Dict[str, Any]],
        python_records: List[Dict[str, Any]],
        java_records: List[Dict[str, Any]],
        split: str,
        dataset_label: str,
    ) -> List[AlignmentRecord]:
        """Exact normalized-NL fallback used only if embeddings are unavailable."""
        py_by_key: Dict[str, List[Dict[str, Any]]] = {}
        for rec in python_records:
            key = _normalize_description(rec.get("natural_language") or rec.get("text") or "")
            if key:
                py_by_key.setdefault(key, []).append(rec)

        java_by_key: Dict[str, List[Dict[str, Any]]] = {}
        for rec in java_records:
            key = _normalize_description(rec.get("natural_language") or rec.get("text") or "")
            if key:
                java_by_key.setdefault(key, []).append(rec)

        records: List[AlignmentRecord] = []
        seen: set = set()

        for nl_rec in nl_records:
            nl = (nl_rec.get("natural_language") or "").strip()
            key = _normalize_description(nl)
            if not key:
                continue
            for py_rec in py_by_key.get(key, [])[:1]:
                for java_rec in java_by_key.get(key, [])[:1]:
                    python_code = (py_rec.get("python_code") or py_rec.get("code") or "").strip()
                    java_code = (java_rec.get("java_code") or java_rec.get("code") or "").strip()
                    if not python_code or not java_code:
                        continue
                    aid = stable_id("fallback", dataset_label, split, key, python_code[:120], java_code[:120])
                    if aid in seen:
                        continue
                    seen.add(aid)
                    records.append(
                        AlignmentRecord(
                            alignment_id=aid,
                            natural_language=nl,
                            python_code=python_code,
                            java_code=java_code,
                            confidence=self.config.alignment.within_dataset_confidence,
                            alignment_strategy="exact_normalized_nl_fallback",
                            python_ast_metadata=_python_ast_metadata(python_code),
                            java_structural_metadata=_java_structural_metadata(java_code),
                            provenance={
                                "dataset": dataset_label,
                                "split": split,
                                "alignment_key": key,
                                "fallback_reason": "embedding_unavailable",
                            },
                            split=split,
                        )
                    )
        return records

    # --------------------------------------------------------
    # XLCoST
    # --------------------------------------------------------

    def align_xlcost(
        self,
        xlcost_python_splits: Dict[str, List[Dict[str, Any]]],
        xlcost_java_splits: Dict[str, List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        SectionPrinter.header("Semantic Alignment — XLCoST")
        all_records: List[AlignmentRecord] = []
        threshold = self.config.alignment.confidence_threshold

        for split in sorted(set(xlcost_python_splits.keys()) & set(xlcost_java_splits.keys())):
            py_rows = xlcost_python_splits[split]
            java_rows = xlcost_java_splits[split]

            nl_seen: set = set()
            nl_records: List[Dict[str, Any]] = []
            for source_name, source_rows in (("python", py_rows), ("java", java_rows)):
                for idx, row in enumerate(source_rows):
                    nl = (row.get("natural_language") or row.get("text") or "").strip()
                    key = _normalize_description(nl)
                    if nl and key not in nl_seen:
                        nl_seen.add(key)
                        nl_records.append({
                            "natural_language": nl,
                            "_record_id": f"xlcost_{source_name}_nl_{split}_{idx}",
                        })

            python_records = [
                {
                    "python_code": row.get("python_code") or row.get("code") or "",
                    "natural_language": row.get("natural_language") or row.get("text") or "",
                    "_record_id": row.get("_record_id", f"xlcost_py_{split}_{idx}"),
                }
                for idx, row in enumerate(py_rows)
            ]
            java_records = [
                {
                    "java_code": row.get("java_code") or row.get("code") or "",
                    "natural_language": row.get("natural_language") or row.get("text") or "",
                    "_record_id": row.get("_record_id", f"xlcost_java_{split}_{idx}"),
                }
                for idx, row in enumerate(java_rows)
            ]

            LOG.info(f"[{split}] Pools — NL: {len(nl_records)}  Python: {len(python_records)}  Java: {len(java_records)}")
            split_records = self.align(
                nl_records,
                python_records,
                java_records,
                split,
                dataset_label="XLCoST",
                strategy="xlcost_semantic_embedding",
            )
            all_records.extend(split_records)
            LOG.info(f"[{split}] Semantic triples formed: {len(split_records)}")

        accepted = [r for r in all_records if r.confidence >= threshold]
        self._save_alignment_analytics()

        SummaryPrinter.print_summary(
            "XLCoST Alignment Summary",
            {
                "Total triples": len(all_records),
                "Above threshold": len(accepted),
                "Confidence threshold": threshold,
                "Strategy": "xlcost_semantic_embedding",
                "Tree-sitter Java": _TS_AVAILABLE,
            },
        )
        return [self._record_to_dict(r) for r in accepted]

    # --------------------------------------------------------
    # CodeXGLUE
    # --------------------------------------------------------

    def align_codexglue(
        self,
        python_splits: Dict[str, List[Dict[str, Any]]],
        java_splits: Dict[str, List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Aligns CodeXGLUE Python and Java records by docstring semantics.

        High-confidence matches become CandidateRows. Unmatched or
        low-confidence evidence is persisted to the teacher completion queue.
        """
        SectionPrinter.header("Semantic Alignment — CodeXGLUE")
        threshold = self.config.alignment.confidence_threshold
        all_records: List[AlignmentRecord] = []

        for split in sorted(set(python_splits.keys()) & set(java_splits.keys())):
            py_rows = python_splits[split]
            java_rows = java_splits[split]

            python_records: List[Dict[str, Any]] = []
            for idx, row in enumerate(py_rows):
                nl = (row.get("natural_language") or row.get("docstring") or row.get("text") or "").strip()
                code = (row.get("python_code") or row.get("code") or "").strip()
                if nl and code:
                    python_records.append({
                        "natural_language": nl,
                        "python_code": code,
                        "_record_id": row.get("_record_id", f"codexglue_py_{split}_{idx}"),
                    })

            java_records: List[Dict[str, Any]] = []
            for idx, row in enumerate(java_rows):
                nl = (row.get("natural_language") or row.get("docstring") or row.get("text") or "").strip()
                code = (row.get("java_code") or row.get("code") or "").strip()
                if nl and code:
                    java_records.append({
                        "natural_language": nl,
                        "java_code": code,
                        "_record_id": row.get("_record_id", f"codexglue_java_{split}_{idx}"),
                    })

            LOG.info(f"[{split}] CodeXGLUE evidence — Python: {len(python_records)}  Java: {len(java_records)}")

            if not python_records or not java_records:
                continue

            py_texts = [r["natural_language"] for r in python_records]
            java_texts = [r["natural_language"] for r in java_records]
            py_emb = self._embed(py_texts)
            java_emb = self._embed(java_texts)

            if py_emb is None or java_emb is None:
                LOG.warning(f"[{split}] CodeXGLUE embeddings unavailable. Skipping forced cross-language matching.")
                continue

            sim = _cosine_matrix(py_emb, java_emb)
            used_java: set = set()
            accepted = 0
            below_threshold = 0
            accepted_scores: List[float] = []

            for i, py_rec in enumerate(python_records):
                best_java_idx = int(np.argmax(sim[i]))
                best_score = float(sim[i, best_java_idx])

                if best_score < threshold:
                    below_threshold += 1
                    self.teacher_completion_queue.append({
                        "queue_id": stable_id("teacher_queue", "codexglue", split, "python", py_rec.get("_record_id", "")),
                        "dataset": "CodeXGLUE",
                        "split": split,
                        "available_modalities": ["natural_language", "python"],
                        "missing_modality": "java",
                        "natural_language": py_rec["natural_language"],
                        "python_code": py_rec["python_code"],
                        "java_code": "",
                        "reason": "no_high_confidence_java_match",
                        "best_similarity": round(best_score, 4),
                        "source_record_id": py_rec.get("_record_id", ""),
                    })
                    continue

                if best_java_idx in used_java:
                    self.teacher_completion_queue.append({
                        "queue_id": stable_id("teacher_queue", "codexglue", split, "python_duplicate", py_rec.get("_record_id", "")),
                        "dataset": "CodeXGLUE",
                        "split": split,
                        "available_modalities": ["natural_language", "python"],
                        "missing_modality": "java",
                        "natural_language": py_rec["natural_language"],
                        "python_code": py_rec["python_code"],
                        "java_code": "",
                        "reason": "best_java_match_already_used",
                        "best_similarity": round(best_score, 4),
                        "source_record_id": py_rec.get("_record_id", ""),
                    })
                    continue

                java_rec = java_records[best_java_idx]
                used_java.add(best_java_idx)

                python_code = py_rec["python_code"].strip()
                java_code = java_rec["java_code"].strip()
                nl = py_rec["natural_language"].strip()

                py_meta = _python_ast_metadata(python_code)
                java_meta = _java_structural_metadata(java_code)
                structural_bonus = _structural_compatibility(py_meta, java_meta, self.config.alignment.structural_bonus)
                confidence = min(1.0, best_score + structural_bonus)

                aid = stable_id("codexglue", split, nl[:120], python_code[:120], java_code[:120])
                all_records.append(
                    AlignmentRecord(
                        alignment_id=aid,
                        natural_language=nl,
                        python_code=python_code,
                        java_code=java_code,
                        confidence=confidence,
                        alignment_strategy="codexglue_docstring_embedding",
                        python_ast_metadata=py_meta,
                        java_structural_metadata=java_meta,
                        provenance={
                            "dataset": "CodeXGLUE",
                            "split": split,
                            "py_record_id": py_rec.get("_record_id", ""),
                            "java_record_id": java_rec.get("_record_id", ""),
                            "docstring_similarity": round(best_score, 4),
                            "structural_bonus": round(structural_bonus, 4),
                            "alignment_note": "High-confidence CodeXGLUE docstring semantic match.",
                        },
                        split=split,
                    )
                )
                accepted += 1
                accepted_scores.append(confidence)

            # Java evidence not used by accepted matches also enters teacher queue.
            for j, java_rec in enumerate(java_records):
                if j not in used_java:
                    self.teacher_completion_queue.append({
                        "queue_id": stable_id("teacher_queue", "codexglue", split, "java", java_rec.get("_record_id", "")),
                        "dataset": "CodeXGLUE",
                        "split": split,
                        "available_modalities": ["natural_language", "java"],
                        "missing_modality": "python",
                        "natural_language": java_rec["natural_language"],
                        "python_code": "",
                        "java_code": java_rec["java_code"],
                        "reason": "not_used_in_high_confidence_match",
                        "source_record_id": java_rec.get("_record_id", ""),
                    })

            self.last_alignment_analytics.append({
                "dataset": "CodeXGLUE",
                "split": split,
                "strategy": "codexglue_docstring_embedding",
                "python_records": len(python_records),
                "java_records": len(java_records),
                "accepted": accepted,
                "below_threshold": below_threshold,
                "unmatched_python_for_teacher": len(python_records) - accepted,
                "unmatched_java_for_teacher": len(java_records) - len(used_java),
                "threshold": threshold,
                "mean_accepted_confidence": float(np.mean(accepted_scores)) if accepted_scores else 0.0,
                "min_accepted_confidence": float(np.min(accepted_scores)) if accepted_scores else 0.0,
                "max_accepted_confidence": float(np.max(accepted_scores)) if accepted_scores else 0.0,
                "tree_sitter_available": _TS_AVAILABLE,
                "tree_sitter_error": _TS_INIT_ERROR,
            })

            LOG.info(
                f"[{split}] CodeXGLUE accepted triples: {accepted} | "
                f"below threshold: {below_threshold} | "
                f"teacher queue py/java: {len(python_records) - accepted}/{len(java_records) - len(used_java)}"
            )

        accepted_records = [r for r in all_records if r.confidence >= threshold]
        self._save_teacher_queue()
        self._save_alignment_analytics()

        SummaryPrinter.print_summary(
            "CodeXGLUE Alignment Summary",
            {
                "Accepted triples": len(accepted_records),
                "Confidence threshold": threshold,
                "Strategy": "codexglue_docstring_embedding",
                "Tree-sitter Java": _TS_AVAILABLE,
                "Teacher queue rows": len(self.teacher_completion_queue),
            },
        )

        return [self._record_to_dict(r) for r in accepted_records]

    # --------------------------------------------------------
    # Inspection helpers
    # --------------------------------------------------------

    def tree_sitter_available(self) -> bool:
        return _TS_AVAILABLE

    def tree_sitter_error(self) -> Optional[str]:
        return _TS_INIT_ERROR
