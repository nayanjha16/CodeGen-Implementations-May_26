"""Read-only SQL safety gate — SELECT and WITH only."""

from __future__ import annotations

import re
from typing import Any

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML

from src.text2sql.sql_validator import SQLValidator

_BLOCKED_KEYWORDS = frozenset(
    {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "REPLACE",
        "MERGE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
    }
)

_ALLOWED = frozenset({"SELECT", "WITH"})


def _first_keyword(statement: Statement) -> str | None:
    for token in statement.tokens:
        if token.ttype is DML:
            return token.value.upper()
        if token.ttype is Keyword:
            value = token.value.upper()
            if value in _ALLOWED or value in _BLOCKED_KEYWORDS:
                return value
    stripped = statement.value.strip().upper()
    for kw in ("SELECT", "WITH", *sorted(_BLOCKED_KEYWORDS)):
        if stripped.startswith(kw + " ") or stripped == kw:
            return kw
    return None


class SafetyValidator:
    """Validate SQL is read-only before execution."""

    def __init__(self):
        self.syntax_validator = SQLValidator()

    def validate(self, sql: str) -> dict[str, Any]:
        sql = sql.strip()
        if not sql:
            return {"passed": False, "message": "Empty SQL query", "reason": "empty"}

        parsed = sqlparse.parse(sql)
        if not parsed:
            return {"passed": False, "message": "Unable to parse SQL", "reason": "parse_error"}

        if len(parsed) > 1:
            return {"passed": False, "message": "Multi-statement batches are not allowed", "reason": "multi_statement"}

        stmt_type = _first_keyword(parsed[0])
        if stmt_type not in _ALLOWED:
            blocked = stmt_type or "unknown"
            return {
                "passed": False,
                "message": f"Blocked non-SELECT statement ({blocked})",
                "reason": f"{blocked} detected",
            }

        upper = sql.upper()
        for kw in _BLOCKED_KEYWORDS:
            if re.search(rf"\b{kw}\b", upper):
                if kw not in ("SELECT", "WITH"):
                    return {
                        "passed": False,
                        "message": f"Blocked non-SELECT statement ({kw})",
                        "reason": f"{kw} detected",
                    }

        syntax = self.syntax_validator.validate_syntax(sql)
        if not syntax["valid"]:
            return {"passed": False, "message": syntax.get("error", "Syntax error"), "reason": "syntax_error"}

        completeness = self.syntax_validator.validate_completeness(sql)
        if not completeness["complete"]:
            issues = ", ".join(completeness["issues"])
            return {"passed": False, "message": f"Incomplete query: {issues}", "reason": "incomplete"}

        return {"passed": True, "message": "Validation passed", "reason": None, "formatted": syntax.get("formatted")}
