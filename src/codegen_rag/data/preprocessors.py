"""Cleaning, filtering, deduplication, and train/val/test splitting.

These functions take raw downloaded data (git clones, jsonl caches) and turn
them into clean, deduplicated records ready for tokenization and task-specific
dataset construction. Every function is pure (no I/O side effects beyond
reading its inputs) so it is trivially unit-testable.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)

_DOCSTRING_PATTERNS = {
    "python": re.compile(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'', re.DOTALL),
    "java": re.compile(r"/\*\*(.*?)\*/", re.DOTALL),
    "cpp": re.compile(r"/\*\*(.*?)\*/", re.DOTALL),
}


@dataclass
class CodeDocRecord:
    """One (code, docstring, language) triple used across Task 1 sub-tasks."""

    code: str
    docstring: str
    language: str
    function_name: str = ""
    source_file: str = ""
    commit_diff: str | None = None
    commit_message: str | None = None
    intent: str = field(default="")

    def content_hash(self) -> str:
        return hashlib.sha256(self.code.strip().encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "docstring": self.docstring,
            "language": self.language,
            "function_name": self.function_name,
            "source_file": self.source_file,
            "commit_diff": self.commit_diff,
            "commit_message": self.commit_message,
            "intent": self.intent,
        }


def strip_docstring(code: str, language: str) -> tuple[str, str]:
    """Split a function into (code_without_docstring, extracted_docstring)."""
    pattern = _DOCSTRING_PATTERNS.get(language.lower())
    if pattern is None:
        return code, ""
    match = pattern.search(code)
    if not match:
        return code, ""
    docstring = next((g for g in match.groups() if g), "").strip()
    code_wo_doc = code[: match.start()] + code[match.end() :]
    return code_wo_doc.strip(), docstring


def extract_function_name(code: str, language: str) -> str:
    """Best-effort function-name extraction via regex (avoids a full parser dependency)."""
    patterns = {
        "python": r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        "java": r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        "cpp": r"[\w:<>\*&]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{]*\)\s*\{",
    }
    pattern = patterns.get(language.lower())
    if not pattern:
        return ""
    match = re.search(pattern, code)
    return match.group(1) if match else ""


def clean_code_text(code: str, min_len: int, max_len: int) -> str | None:
    """Normalize whitespace and reject degenerate samples; returns None to drop."""
    if not code or not code.strip():
        return None
    normalized = code.replace("\r\n", "\n").replace("\t", "    ").strip()
    if not (min_len <= len(normalized) <= max_len):
        return None
    return normalized


def deduplicate(records: list[CodeDocRecord]) -> list[CodeDocRecord]:
    """Drop records with duplicate code content, keeping the first occurrence."""
    seen: set[str] = set()
    unique: list[CodeDocRecord] = []
    for record in records:
        h = record.content_hash()
        if h in seen:
            continue
        seen.add(h)
        unique.append(record)
    logger.info("Deduplicated %d -> %d records", len(records), len(unique))
    return unique


def parse_codocbench_directory(
    root: Path,
    languages: list[str],
    min_len: int = 20,
    max_len: int = 8000,
) -> list[CodeDocRecord]:
    """Walk a cloned CoDocBench repository and extract (code, docstring, diff) triples.

    CoDocBench's actual release layout (see https://github.com/kunpai/codocbench)
    is a single ``dataset/codocbench.jsonl`` file (plus ``dataset/train.jsonl``
    / ``dataset/test.jsonl``), *not* per-language files under
    ``data/<language>/*.json*`` -- and the dataset is Python-only (4,573
    pairs from 200 Python projects; there is no Java/C++ split at all), so
    only ``language == "python"`` will ever yield records from it. Each line
    is also shaped with the code/docstring nested two levels deep::

        {"file": ..., "function": "fully.qualified.name",
         "version_data": [{"code": ..., "docstring": ..., "commit_message": ...}, ...],
         "diff_code": ..., "file_path": ..., "project": ...}

    rather than as flat top-level ``code``/``docstring`` keys. This parser
    handles that real shape, while still tolerating a flat
    ``data/<language>/*.json*`` layout (other CodeDocRecord-style sources, or
    a hand-rolled subset) for backward compatibility. It skips malformed
    entries/files with a warning rather than crashing the whole pipeline.
    """
    records: list[CodeDocRecord] = []
    for language in languages:
        candidates: list[Path] = []

        if language.lower() == "python":
            dataset_dir = root / "dataset"
            for name in ("codocbench.jsonl", "train.jsonl", "test.jsonl"):
                candidate = dataset_dir / name
                if candidate.exists():
                    candidates.append(candidate)

        lang_dir = root / "data" / language
        if lang_dir.exists():
            candidates += list(lang_dir.rglob("*.json")) + list(lang_dir.rglob("*.jsonl"))
        elif not candidates:
            # Fall back to scanning the whole repo for files whose name hints
            # at this language, since dataset layouts change between releases.
            candidates += list(root.rglob(f"*{language}*.json")) + list(
                root.rglob(f"*{language}*.jsonl")
            )

        for file_path in candidates:
            try:
                raw_entries = _load_json_or_jsonl(file_path)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                logger.warning("Skipping malformed file %s: %s", file_path, exc)
                continue

            for entry in raw_entries:
                records.extend(_codocbench_records_from_entry(entry, language, file_path, root, min_len, max_len))

    logger.info("Parsed %d raw CoDocBench records across %s", len(records), languages)
    return deduplicate(records)


def _codocbench_records_from_entry(
    entry: dict[str, Any],
    language: str,
    file_path: Path,
    root: Path,
    min_len: int,
    max_len: int,
) -> list[CodeDocRecord]:
    """Build zero or more `CodeDocRecord`s from one raw JSON entry, handling
    both CoDocBench's real nested ``version_data`` shape and a flat
    ``{"code": ..., "docstring": ...}`` shape."""
    try:
        rel_source = str(file_path.relative_to(root))
    except ValueError:
        rel_source = str(file_path)

    version_data = entry.get("version_data")
    if isinstance(version_data, list) and version_data:
        out: list[CodeDocRecord] = []
        for version in version_data:
            if not isinstance(version, dict):
                continue
            code = version.get("code")
            if not code:
                continue
            cleaned = clean_code_text(code, min_len, max_len)
            if cleaned is None:
                continue
            docstring = str(version.get("docstring") or "").strip()
            out.append(
                CodeDocRecord(
                    code=cleaned,
                    docstring=docstring,
                    language=language,
                    function_name=str(entry.get("function", "")).split(".")[-1],
                    source_file=str(entry.get("file_path") or entry.get("file") or rel_source),
                    commit_diff=entry.get("diff_code"),
                    commit_message=version.get("commit_message"),
                    # "intent" is the natural-language prompt used downstream to drive
                    # generation (see tasks/program_synthesis.py); the docstring is the
                    # closest thing CoDocBench provides to a task description.
                    intent=docstring,
                )
            )
        return out

    # Flat shape: {"code"/"old_code": ..., "docstring"/"documentation": ...}
    code = entry.get("code") or entry.get("old_code")
    doc = entry.get("docstring") or entry.get("documentation") or ""
    if not code:
        return []
    cleaned = clean_code_text(code, min_len, max_len)
    if cleaned is None:
        return []
    return [
        CodeDocRecord(
            code=cleaned,
            docstring=str(doc).strip(),
            language=language,
            function_name=extract_function_name(cleaned, language),
            source_file=rel_source,
            commit_diff=entry.get("diff"),
            commit_message=entry.get("commit_message") or entry.get("commit_msg"),
            intent=str(entry.get("intent") or doc).strip(),
        )
    ]


def _load_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    parsed = json.loads(text)
    if isinstance(parsed, dict):
        # Some releases nest records under a top-level key.
        for value in parsed.values():
            if isinstance(value, list):
                return value
        return [parsed]
    return parsed


def train_val_test_split(
    records: list[Any],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[Any]]:
    """Deterministic shuffle-then-split into train/val/test partitions."""
    rng = random.Random(seed)
    shuffled = records.copy()
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    return {
        "train": shuffled[:n_train],
        "val": shuffled[n_train : n_train + n_val],
        "test": shuffled[n_train + n_val :],
    }


def clean_rust_corpus(
    raw_samples: list[dict[str, Any]],
    min_len: int = 20,
    max_len: int = 8000,
) -> list[dict[str, Any]]:
    """Filter and normalize raw Rust source snippets prior to fine-tuning."""
    cleaned: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for sample in raw_samples:
        code = clean_code_text(sample.get("code", ""), min_len, max_len)
        if code is None:
            continue
        h = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        cleaned.append({**sample, "code": code})
    logger.info("Cleaned Rust corpus: %d -> %d samples", len(raw_samples), len(cleaned))
    return cleaned


def mix_anti_forgetting_samples(
    target_language_samples: list[dict[str, Any]],
    source_language_samples: list[dict[str, Any]],
    anti_forgetting_ratio: float = 0.15,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Mix in a fraction of source-language (e.g. Python) samples to reduce
    catastrophic forgetting during new-language fine-tuning (Task 4)."""
    rng = random.Random(seed)
    n_target = len(target_language_samples)
    n_source = int(n_target * anti_forgetting_ratio / max(1e-9, (1 - anti_forgetting_ratio)))
    n_source = min(n_source, len(source_language_samples))

    source_subset = rng.sample(source_language_samples, n_source) if n_source > 0 else []
    combined = target_language_samples + source_subset
    rng.shuffle(combined)
    logger.info(
        "Mixed %d target + %d source (%.1f%%) samples for anti-forgetting training",
        n_target,
        n_source,
        100 * n_source / max(1, len(combined)),
    )
    return combined
