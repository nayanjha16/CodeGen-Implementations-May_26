"""Minimal MongoDB shell query parser (TEND-compatible subset)."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any

_SUPPORTED_METHODS = frozenset({"find", "aggregate", "countdocuments", "distinct"})


class ShellParseError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedShellQuery:
    collection: str
    method: str
    args: tuple[Any, ...] = ()
    sort: dict[str, Any] | None = None
    skip: int | None = None
    limit: int | None = None


_CHAIN_RE = re.compile(
    r"\.sort\s*\((\{.*?\})\)\s*"
    r"(?:\.skip\s*\((\d+)\)\s*)?"
    r"(?:\.limit\s*\((\d+)\)\s*)?",
    re.IGNORECASE | re.DOTALL,
)
_QUERY_RE = re.compile(
    r"^\s*db\.(\w+)\.(find|aggregate|countDocuments|distinct)\s*\((.*)\)\s*(.*)?$",
    re.IGNORECASE | re.DOTALL,
)


def _parse_python_literal(text: str) -> Any:
    text = text.strip()
    if not text:
        return None
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise ShellParseError(f"Invalid literal: {text[:80]}") from exc


def _split_top_level_args(args_text: str) -> list[str]:
    args_text = args_text.strip()
    if not args_text:
        return []
    parts: list[str] = []
    depth = 0
    start = 0
    for index, ch in enumerate(args_text):
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(args_text[start:index].strip())
            start = index + 1
    parts.append(args_text[start:].strip())
    return [part for part in parts if part]


def parse_shell_query(query: str) -> ParsedShellQuery:
    text = (query or "").strip().rstrip(";")
    match = _QUERY_RE.match(text)
    if not match:
        raise ShellParseError(
            "Expected format: db.collection.find({...}) or db.collection.aggregate([...])"
        )

    collection = match.group(1)
    method = match.group(2).lower()
    if method not in _SUPPORTED_METHODS:
        raise ShellParseError(f"Unsupported method: {method}")

    args_text = match.group(3).strip()
    chain = (match.group(4) or "").strip()
    arg_parts = _split_top_level_args(args_text)
    args = tuple(_parse_python_literal(part) for part in arg_parts)

    sort: dict[str, Any] | None = None
    skip: int | None = None
    limit: int | None = None
    if chain:
        chain_match = _CHAIN_RE.search(chain)
        if chain_match:
            sort = _parse_python_literal(chain_match.group(1))
            if chain_match.group(2):
                skip = int(chain_match.group(2))
            if chain_match.group(3):
                limit = int(chain_match.group(3))

    return ParsedShellQuery(
        collection=collection,
        method=method,
        args=args,
        sort=sort,
        skip=skip,
        limit=limit,
    )
