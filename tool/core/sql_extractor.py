"""Extract SQL from model/API output without loading the model."""

from __future__ import annotations

import re


class SqlExtractor:
    """Reuse SQLGenerator extraction patterns without model dependencies."""

    _SELECT_FROM_RE = re.compile(r"^\s*SELECT\b.+\bFROM\b", re.IGNORECASE | re.DOTALL)
    _NON_SQL_MARKER_RE = re.compile(
        r"\n(?:Output:|MongoDB:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|SQL:\n)",
        re.IGNORECASE,
    )
    _NON_SQL_LINE_RE = re.compile(
        r"^(?:Output:|MongoDB:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|conn\s*=|for\s+\w+\s+in|print\s*\(|SQL:)",
        re.IGNORECASE,
    )
    _SQL_KEYWORD_LINE_RE = re.compile(
        r"^(?:SELECT|FROM|WHERE|GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT|OFFSET|"
        r"JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|ON|AND|OR|UNION|WITH|"
        r"DISTINCT|\)|\(|,)",
        re.IGNORECASE,
    )
    _SQL_FRAGMENT_LINE_RE = re.compile(r"^[\w\s.*'\",=<>!+\-/%()?;[\]]+$")

    def _looks_like_sql(self, text: str) -> bool:
        text = text.strip()
        return bool(text and self._SELECT_FROM_RE.match(text))

    def _trim_non_sql_suffix(self, text: str) -> str:
        match = self._NON_SQL_MARKER_RE.search(text)
        if match:
            text = text[: match.start()]
        return text.strip()

    def _is_sql_fragment_line(self, line: str) -> bool:
        if self._NON_SQL_LINE_RE.match(line):
            return False
        if self._SQL_KEYWORD_LINE_RE.match(line):
            return True
        return bool(self._SQL_FRAGMENT_LINE_RE.match(line))

    def _normalize_sql(self, sql: str) -> str:
        return re.sub(r"\s+", " ", sql).strip()

    def _extract_multiline_select(self, text: str) -> str:
        text = self._trim_non_sql_suffix(text)
        if not re.match(r"^\s*SELECT\b", text, re.IGNORECASE):
            return ""

        lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                if lines:
                    break
                continue
            if lines and not self._is_sql_fragment_line(stripped):
                break
            if (
                lines
                and re.match(r"^SELECT\b", stripped, re.IGNORECASE)
                and self._looks_like_sql(self._normalize_sql(" ".join(lines)))
            ):
                break
            if not lines and not re.match(r"^SELECT\b", stripped, re.IGNORECASE):
                continue
            lines.append(stripped)

        if not lines:
            return ""
        candidate = self._normalize_sql(" ".join(lines))
        return candidate if self._looks_like_sql(candidate) else ""

    def extract(self, raw_output: str) -> str:
        """Extract SQL from model output text."""
        text = self._trim_non_sql_suffix(raw_output.strip())

        code_match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if code_match:
            candidate = self._normalize_sql(code_match.group(1))
            if self._looks_like_sql(candidate):
                return candidate
            if re.match(r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", candidate, re.IGNORECASE):
                return candidate

        multiline = self._extract_multiline_select(text)
        if multiline:
            return multiline

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines:
            if self._looks_like_sql(line):
                return line
            if re.match(r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", line, re.IGNORECASE):
                return line

        if self._looks_like_sql(text):
            return self._normalize_sql(text)
        return ""


def extract_sql(raw_output: str) -> str:
    """Convenience wrapper."""
    return SqlExtractor().extract(raw_output)
