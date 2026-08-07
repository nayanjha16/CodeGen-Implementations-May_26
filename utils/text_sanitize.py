"""Text cleanup helpers for LLM outputs."""

from __future__ import annotations

import re

_ROLEPLAY_MARKER_RE = re.compile(
    r"(?:^|[\n\r]|(?<=[.!?])|\s)(Human|User|AI|Assistant)\s*:",
    re.IGNORECASE,
)


def truncate_roleplay_continuation(text: str) -> str:
    """Drop fake multi-turn dialogue appended after the real answer."""
    raw = (text or "").strip()
    if not raw:
        return ""
    match = _ROLEPLAY_MARKER_RE.search(raw)
    if not match:
        return raw
    if match.start() == 0:
        return ""
    return raw[: match.start()].strip()
