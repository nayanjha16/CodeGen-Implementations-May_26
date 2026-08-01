"""Dependency-free normalization of model completions.

Raw generations are always retained by callers.  These helpers produce the
bounded answer that is displayed, validated, and scored.  They deliberately
perform extraction rather than semantic repair: markdown/meta sections,
duplicated tails, and text emitted after a complete Java compilation unit are
removed, but missing algorithms or identifiers are never invented.
"""

from __future__ import annotations

import ast
import re


_SECTION_START = re.compile(r"(?m)^\s*###\s+")
_FENCE = re.compile(
    r"```(?P<language>python|py|java)?\s*(?P<body>.*?)```",
    flags=re.IGNORECASE | re.DOTALL,
)


def _clean_common(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    # XLCoST uses the SentencePiece whitespace marker in output literals.
    # It is presentation metadata, not part of Python or Java source.
    # Handle both the real SentencePiece marker and its common UTF-8/
    # Windows-1252 mojibake representation in older exported datasets.
    text = text.replace("▁", " ").replace("â–", " ")
    text = re.sub(
        r"^\s*###\s+(?:Python(?:\s+Translation)?|Java(?:\s+Translation)?|Explanation)\s*\n",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^(?:Here is|Sure, here is|The code is|Below is)[^\n:]*:\s*",
        "",
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    return text.strip()


def _first_fenced_body(text: str, language: str) -> str | None:
    wanted = "python" if language.lower() in {"python", "py"} else "java"
    fallback = None
    for match in _FENCE.finditer(text):
        label = (match.group("language") or "").lower()
        body = match.group("body").strip()
        fallback = fallback or body
        if label in {wanted, "py" if wanted == "python" else wanted}:
            return body
    return fallback


def _cut_generated_sections(text: str) -> str:
    markers = (
        "Explanation:",
        "Python:",
        "Java:",
        "<|im_end|>",
        "<|endoftext|>",
    )
    positions = [text.find(marker) for marker in markers if text.find(marker) >= 0]
    section = _SECTION_START.search(text)
    if section:
        positions.append(section.start())
    fence = text.find("```")
    if fence >= 0:
        positions.append(fence)
    return text[: min(positions)] if positions else text


def _valid_python_prefix(text: str) -> str:
    """Drop only an incomplete trailing line block from Python output."""

    try:
        ast.parse(text)
        return text
    except (SyntaxError, ValueError):
        pass

    lines = text.splitlines()
    for end in range(len(lines) - 1, 0, -1):
        candidate = "\n".join(lines[:end]).rstrip()
        if not candidate or not re.search(r"[A-Za-z0-9_]", candidate):
            continue
        try:
            ast.parse(candidate)
            return candidate
        except (SyntaxError, ValueError):
            continue
    return text


def _complete_java_unit(text: str) -> str:
    """Return through the first balanced top-level Java type declaration."""

    declaration = re.search(
        r"\b(?:class|interface|enum|record)\s+[A-Za-z_][A-Za-z0-9_]*[^\{]*\{",
        text,
    )
    if not declaration:
        return text

    opening = text.find("{", declaration.start())
    depth = 0
    state = "code"
    escaped = False
    index = opening
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "line_comment":
            if char == "\n":
                state = "code"
        elif state == "block_comment":
            if char == "*" and nxt == "/":
                state = "code"
                index += 1
        elif state in {"string", "char"}:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif (state == "string" and char == '"') or (
                state == "char" and char == "'"
            ):
                state = "code"
        else:
            if char == "/" and nxt == "/":
                state = "line_comment"
                index += 1
            elif char == "/" and nxt == "*":
                state = "block_comment"
                index += 1
            elif char == '"':
                state = "string"
            elif char == "'":
                state = "char"
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[: index + 1].rstrip()
        index += 1
    return text


def extract_code(prediction: str, language: str) -> str:
    """Extract a bounded Python or Java answer from a raw completion."""

    text = _clean_common(prediction)
    fenced = _first_fenced_body(text, language)
    if fenced is not None:
        text = fenced
    text = _cut_generated_sections(text).strip()
    if language.lower() in {"python", "py"}:
        text = _valid_python_prefix(text)
    elif language.lower() == "java":
        text = _complete_java_unit(text)
    return text.strip()


def extract_natural_language(prediction: str) -> str:
    """Extract one concise explanation and remove exact repeated clauses."""

    text = _clean_common(prediction)
    fenced = _first_fenced_body(text, "python")
    if fenced is not None and text.lstrip().startswith("```"):
        # A code-only answer violates the NL contract; keep it visible so the
        # output validator can fail it rather than hiding the violation.
        return text.strip()
    section = _SECTION_START.search(text)
    if section:
        text = text[: section.start()]
    text = text.replace("<|im_end|>", "").replace("<|endoftext|>", "").strip()

    # XLCoST task descriptions use semicolon-delimited clauses.  Fine-tuned
    # models can repeat the final clauses until max_new_tokens; retain the
    # first occurrence of each clause while preserving its original order.
    if ";" in text:
        clauses = [clause.strip() for clause in text.split(";")]
        unique = []
        seen = set()
        for clause in clauses:
            key = re.sub(r"\s+", " ", clause).strip(" .").casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(clause)
        text = " ; ".join(unique)
    return re.sub(r"[ \t]+", " ", text).strip()
