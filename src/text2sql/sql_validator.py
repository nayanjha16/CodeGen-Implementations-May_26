"""SQL validation using sqlparse and sqlite parser."""

from __future__ import annotations

import re
import sqlite3
from typing import Any

import sqlparse


class SQLValidator:
    """Validate SQL syntax and query completeness."""

    REQUIRED_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "DELETE", "WITH")

    def validate_syntax(self, sql: str) -> dict[str, Any]:
        """Validate SQL syntax using sqlparse."""
        sql = sql.strip()
        if not sql:
            return {"valid": False, "error": "Empty SQL query"}

        try:
            parsed = sqlparse.parse(sql)
            if not parsed or not parsed[0].tokens:
                return {"valid": False, "error": "Unable to parse SQL"}

            formatted = sqlparse.format(sql, reindent=True, keyword_case="upper")
            has_keyword = any(
                re.search(rf"\b{kw}\b", sql, re.IGNORECASE)
                for kw in self.REQUIRED_KEYWORDS
            )
            if not has_keyword:
                return {"valid": False, "error": "Missing SQL statement keyword"}

            return {"valid": True, "formatted": formatted, "error": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def validate_completeness(self, sql: str) -> dict[str, Any]:
        """Check query completeness (balanced parentheses, non-trivial structure)."""
        sql = sql.strip()
        if not sql:
            return {"complete": False, "issues": ["Empty query"]}

        issues = []
        if sql.count("(") != sql.count(")"):
            issues.append("Unbalanced parentheses")

        upper = sql.upper()
        if "SELECT" in upper and "FROM" not in upper and "VALUES" not in upper:
            issues.append("SELECT without FROM clause")

        if len(sql.split()) < 2:
            issues.append("Query too short to be complete")

        return {"complete": len(issues) == 0, "issues": issues}

    def validate_with_sqlite(self, sql: str, db_path: str | None = None) -> dict[str, Any]:
        """Validate SQL using SQLite EXPLAIN (syntax check without execution)."""
        syntax = self.validate_syntax(sql)
        completeness = self.validate_completeness(sql)

        sqlite_valid = True
        sqlite_error = None
        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                conn.execute(f"EXPLAIN {sql}")
                conn.close()
            except sqlite3.Error as e:
                sqlite_valid = False
                sqlite_error = str(e)

        return {
            "syntax_valid": syntax["valid"],
            "syntax_error": syntax.get("error"),
            "complete": completeness["complete"],
            "completeness_issues": completeness["issues"],
            "sqlite_valid": sqlite_valid,
            "sqlite_error": sqlite_error,
            "valid": syntax["valid"] and completeness["complete"] and sqlite_valid,
        }

    def validate(self, sql: str, db_path: str | None = None) -> dict[str, Any]:
        """Full validation pipeline."""
        return self.validate_with_sqlite(sql, db_path)
