"""Parse MongoDB shell query strings into structured operations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_SUPPORTED_METHODS = frozenset({"find", "aggregate", "countdocuments", "distinct"})


class ShellParseError(ValueError):
    """Raised when a Mongo shell query cannot be parsed."""


@dataclass(frozen=True)
class ParsedShellQuery:
    """Structured representation of ``db.collection.method(...)`` syntax."""

    collection: str
    method: str
    args: tuple[Any, ...] = ()
    sort: dict[str, Any] | None = None
    skip: int | None = None
    limit: int | None = None


def _skip_ws(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _parse_string(text: str, index: int) -> tuple[str, int]:
    quote = text[index]
    if quote not in {"'", '"'}:
        raise ShellParseError(f"Expected string at position {index}")
    index += 1
    chars: list[str] = []
    while index < len(text):
        ch = text[index]
        if ch == "\\" and index + 1 < len(text):
            chars.append(text[index + 1])
            index += 2
            continue
        if ch == quote:
            return "".join(chars), index + 1
        chars.append(ch)
        index += 1
    raise ShellParseError("Unterminated string literal")


def _parse_identifier(text: str, index: int) -> tuple[str, int]:
    start = index
    if text[index] == "$":
        index += 1
    while index < len(text) and (text[index].isalnum() or text[index] in {"_", "$"}):
        index += 1
    if start == index:
        raise ShellParseError(f"Expected identifier at position {index}")
    return text[start:index], index


def _parse_number(text: str, index: int) -> tuple[int | float, int]:
    start = index
    if text[index] == "-":
        index += 1
    while index < len(text) and (text[index].isdigit() or text[index] == "."):
        index += 1
    token = text[start:index]
    if "." in token:
        return float(token), index
    return int(token), index


def _parse_value(text: str, index: int) -> tuple[Any, int]:
    index = _skip_ws(text, index)
    if index >= len(text):
        raise ShellParseError("Unexpected end of input")

    ch = text[index]
    if ch in {"'", '"'}:
        return _parse_string(text, index)
    if ch == "{":
        return _parse_object(text, index)
    if ch == "[":
        return _parse_array(text, index)
    if ch == "-":
        return _parse_number(text, index)
    if ch.isdigit():
        return _parse_number(text, index)

    ident, next_index = _parse_identifier(text, index)
    lowered = ident.lower()
    if lowered == "true":
        return True, next_index
    if lowered == "false":
        return False, next_index
    if lowered in {"null", "undefined"}:
        return None, next_index
    return ident, next_index


def _parse_object(text: str, index: int) -> tuple[dict[str, Any], int]:
    if text[index] != "{":
        raise ShellParseError(f"Expected '{{' at position {index}")
    index += 1
    obj: dict[str, Any] = {}
    index = _skip_ws(text, index)
    if index < len(text) and text[index] == "}":
        return obj, index + 1

    while index < len(text):
        index = _skip_ws(text, index)
        if text[index] in {"'", '"'}:
            key, index = _parse_string(text, index)
        else:
            key, index = _parse_identifier(text, index)
        index = _skip_ws(text, index)
        if index >= len(text) or text[index] != ":":
            raise ShellParseError(f"Expected ':' after key {key!r}")
        index += 1
        value, index = _parse_value(text, index)
        obj[key] = value
        index = _skip_ws(text, index)
        if index >= len(text):
            break
        if text[index] == ",":
            index += 1
            continue
        if text[index] == "}":
            return obj, index + 1
        raise ShellParseError(f"Expected ',' or '}}' at position {index}")
    raise ShellParseError("Unterminated object literal")


def _parse_array(text: str, index: int) -> tuple[list[Any], int]:
    if text[index] != "[":
        raise ShellParseError(f"Expected '[' at position {index}")
    index += 1
    items: list[Any] = []
    index = _skip_ws(text, index)
    if index < len(text) and text[index] == "]":
        return items, index + 1

    while index < len(text):
        value, index = _parse_value(text, index)
        items.append(value)
        index = _skip_ws(text, index)
        if index >= len(text):
            break
        if text[index] == ",":
            index += 1
            continue
        if text[index] == "]":
            return items, index + 1
        raise ShellParseError(f"Expected ',' or ']' at position {index}")
    raise ShellParseError("Unterminated array literal")


def _split_top_level_args(text: str) -> list[str]:
    args: list[str] = []
    depth_paren = depth_brace = depth_bracket = 0
    in_string: str | None = None
    start = 0
    for index, ch in enumerate(text):
        if in_string:
            if ch == "\\":
                continue
            if ch == in_string:
                in_string = None
            continue
        if ch in {"'", '"'}:
            in_string = ch
            continue
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        elif ch == "," and depth_paren == depth_brace == depth_bracket == 0:
            args.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        args.append(tail)
    return args


def _parse_args(arg_text: str) -> tuple[Any, ...]:
    arg_text = arg_text.strip()
    if not arg_text:
        return ()
    parts = _split_top_level_args(arg_text)
    parsed: list[Any] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        value, end = _parse_value(part, 0)
        if _skip_ws(part, end) != len(part):
            raise ShellParseError(f"Unexpected trailing content in argument: {part!r}")
        parsed.append(value)
    return tuple(parsed)


def _parse_chain(text: str) -> tuple[dict[str, Any], int | None, int | None]:
    sort_spec: dict[str, Any] | None = None
    skip: int | None = None
    limit: int | None = None
    for match in re.finditer(r"\.(sort|skip|limit)\s*\(", text, re.IGNORECASE):
        method = match.group(1).lower()
        open_paren = match.end() - 1
        depth = 0
        in_string: str | None = None
        close_paren = None
        for index in range(open_paren, len(text)):
            ch = text[index]
            if in_string:
                if ch == "\\":
                    continue
                if ch == in_string:
                    in_string = None
                continue
            if ch in {"'", '"'}:
                in_string = ch
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    close_paren = index
                    break
        if close_paren is None:
            raise ShellParseError(f"Unterminated chain call .{method}(")
        arg_text = text[open_paren + 1 : close_paren]
        args = _parse_args(arg_text)
        if method == "sort":
            if not args or not isinstance(args[0], dict):
                raise ShellParseError(".sort() expects an object argument")
            sort_spec = args[0]
        elif method == "skip":
            if not args or not isinstance(args[0], int):
                raise ShellParseError(".skip() expects an integer argument")
            skip = args[0]
        elif method == "limit":
            if not args or not isinstance(args[0], int):
                raise ShellParseError(".limit() expects an integer argument")
            limit = args[0]
    return sort_spec, skip, limit


def parse_shell_query(query: str) -> ParsedShellQuery:
    """Parse ``db.collection.method(...)`` shell syntax with optional chaining."""
    text = (query or "").strip()
    if not text:
        raise ShellParseError("Empty MongoDB query")

    match = re.match(
        r"^\s*db\.(\w+)\.(find|aggregate|countDocuments|distinct)\s*\(",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ShellParseError("Query must start with db.<collection>.<method>(")

    collection = match.group(1)
    method = match.group(2).lower()
    if method not in _SUPPORTED_METHODS:
        raise ShellParseError(f"Unsupported MongoDB method: {method}")

    open_paren = match.end() - 1
    depth = 0
    in_string: str | None = None
    close_paren = None
    for index in range(open_paren, len(text)):
        ch = text[index]
        if in_string:
            if ch == "\\":
                continue
            if ch == in_string:
                in_string = None
            continue
        if ch in {"'", '"'}:
            in_string = ch
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                close_paren = index
                break
    if close_paren is None:
        raise ShellParseError("Unterminated method call")

    arg_text = text[open_paren + 1 : close_paren]
    args = _parse_args(arg_text)
    sort_spec, skip, limit = _parse_chain(text[close_paren + 1 :])
    return ParsedShellQuery(
        collection=collection,
        method=method,
        args=args,
        sort=sort_spec,
        skip=skip,
        limit=limit,
    )
