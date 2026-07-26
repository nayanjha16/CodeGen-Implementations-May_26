"""Reuse model output extractors from src without loading HuggingFace weights."""

from __future__ import annotations

import re

_MONGO_QUERY_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)
_NON_DOC_MARKER_RE = re.compile(
    r"\n(?:MongoDB query:|MongoDB:|SQL:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|```)",
    re.IGNORECASE,
)
_CODE_FENCE_BLOCK_RE = re.compile(
    r"```(?:[\w+-]*)?\s*.*?```",
    re.DOTALL | re.IGNORECASE,
)
_JSON_LIKE_RE = re.compile(
    r"\{[\s\S]*?(?:\$?(?:query|match|group|project|sort|filter|distinct)|\"[\w.]+\")[\s\S]*?\}",
    re.IGNORECASE,
)


def extract_sql(raw_output: str) -> str:
    from src.text2sql.sql_generator import SQLGenerator

    extractor = SQLGenerator.__new__(SQLGenerator)
    return SQLGenerator._extract_sql(extractor, raw_output)


def extract_nosql(raw_output: str) -> str:
    from src.sql2nosql.nosql_generator import NoSQLGenerator

    extractor = NoSQLGenerator.__new__(NoSQLGenerator)
    return NoSQLGenerator._extract_mongodb_query(extractor, raw_output)


def _trim_non_doc_suffix(text: str) -> str:
    match = _NON_DOC_MARKER_RE.search(text)
    if match:
        text = text[: match.start()]
    return text.strip()


def _looks_like_code_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("{", "[", "}", "]", "```")):
        return True
    if _MONGO_QUERY_RE.search(stripped):
        return True
    if _JSON_LIKE_RE.search(stripped):
        return True
    if stripped.count(":") >= 2 and ('"' in stripped or "'" in stripped):
        return True
    return False


def extract_documentation(raw_output: str) -> str:
    """Mirrors src.documentation.doc_generator.extract_documentation_from_output."""
    text = _trim_non_doc_suffix(raw_output.strip())
    text = _CODE_FENCE_BLOCK_RE.sub("", text)

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```") or _looks_like_code_line(stripped):
            break
        if _MONGO_QUERY_RE.search(stripped):
            break
        if stripped.lower().startswith(
            ("documentation:", "output:", "answer:", "response:")
        ):
            stripped = re.sub(
                r"^(?:documentation|output|answer|response)\s*:\s*",
                "",
                stripped,
                flags=re.IGNORECASE,
            )
        if stripped and not _looks_like_code_line(stripped):
            lines.append(stripped)

    return " ".join(lines).strip()
