"""Extract plain-English documentation from model/API output."""

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
_HEADING_RE = re.compile(r"^#+\s*", re.MULTILINE)


def _trim_non_doc_suffix(text: str) -> str:
    match = _NON_DOC_MARKER_RE.search(text)
    if match:
        text = text[: match.start()]
    return text.strip()


def _looks_like_code_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("db."):
        return True
    if stripped.startswith("{") or stripped.startswith("["):
        return True
    return bool(_MONGO_QUERY_RE.search(stripped))


def extract_documentation(raw_output: str, *, max_chars: int = 500) -> str:
    """Extract concise documentation text from model output."""
    text = _trim_non_doc_suffix(raw_output.strip())
    text = _CODE_FENCE_BLOCK_RE.sub("", text)
    text = _HEADING_RE.sub("", text)

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```") or _looks_like_code_line(stripped):
            break
        if _MONGO_QUERY_RE.search(stripped):
            break
        if stripped.lower().startswith(("documentation:", "output:", "answer:", "response:")):
            stripped = re.sub(
                r"^(?:documentation|output|answer|response)\s*:\s*",
                "",
                stripped,
                flags=re.IGNORECASE,
            )
        lines.append(stripped)

    if not lines:
        candidate = re.sub(r"\s+", " ", text).strip()
    else:
        candidate = " ".join(lines)

    candidate = re.sub(r"\s+", " ", candidate).strip()
    if len(candidate) > max_chars:
        truncated = candidate[: max_chars - 3].rsplit(" ", 1)[0]
        candidate = f"{truncated}..." if truncated else candidate[:max_chars]
    return candidate
