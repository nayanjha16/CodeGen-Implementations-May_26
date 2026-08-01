"""Conservative redaction helpers for persisted/retrieved source evidence."""

from __future__ import annotations

import re

_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b(\s*[:=]\s*)([\"'][^\"'\n]{6,}[\"'])"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)


def redact_secrets(text: str) -> str:
    value = text or ""
    value = _SECRET_PATTERNS[0].sub(r"\1\2\"<REDACTED>\"", value)
    for pattern in _SECRET_PATTERNS[1:]:
        value = pattern.sub("<REDACTED>", value)
    return value
