"""Extract MongoDB shell queries from model/API output."""

from __future__ import annotations

import re

_MONGO_START_RE = re.compile(
    r"db\.\w+\.(?:find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)
_CODE_FENCE_RE = re.compile(
    r"```(?:javascript|mongo|mongodb|js)?\s*(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
_CHAIN_RE = re.compile(
    r"(\s*\.(?:sort|limit|skip|hint)\([^)]*\))+",
    re.IGNORECASE,
)
_NON_MONGO_MARKER_RE = re.compile(
    r"\n(?:Output:|SQL:|MongoDB:|Python\b|JavaScript\b|import\s+|#include\b|\"\"\"|```)",
    re.IGNORECASE,
)


def _trim_non_mongo_suffix(text: str) -> str:
    match = _NON_MONGO_MARKER_RE.search(text)
    if match:
        text = text[: match.start()]
    return text.strip()


def _extract_balanced_call(text: str) -> str:
    depth = 0
    started = False
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
            started = True
        elif char == ")":
            depth -= 1
            if started and depth == 0:
                end = index + 1
                chain = _CHAIN_RE.match(text[end:])
                if chain:
                    end += chain.end()
                return text[:end].strip()
    return text.strip()


def extract_nosql(raw_output: str) -> str:
    """Extract a MongoDB shell query from model output text."""
    text = _trim_non_mongo_suffix(raw_output.strip())

    code_match = _CODE_FENCE_RE.search(text)
    if code_match:
        candidate = code_match.group(1).strip()
        match = _MONGO_START_RE.search(candidate)
        if match:
            return _extract_balanced_call(candidate[match.start() :])

    match = _MONGO_START_RE.search(text)
    if not match:
        return ""

    return _extract_balanced_call(text[match.start() :])
