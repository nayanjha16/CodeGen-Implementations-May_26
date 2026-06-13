"""Rule-based SQL to MongoDB query translator using SQL AST parsing."""

from __future__ import annotations

import logging
import re
from typing import Any

import sqlparse
from sqlparse.sql import Comparison, Identifier, IdentifierList, Parenthesis, Token
from sqlparse.tokens import Keyword, Name

logger = logging.getLogger("codegen")


class SQLToNoSQLTranslator:
    """Translate SQL SELECT queries to MongoDB find() syntax."""

    SUPPORTED = {"SELECT", "WHERE", "ORDER BY", "LIMIT", "GROUP BY"}
    UNSUPPORTED_WARNINGS: list[str] = []

    def translate(self, sql: str) -> dict[str, Any]:
        """Translate SQL to MongoDB query string."""
        self.UNSUPPORTED_WARNINGS = []
        sql = sql.strip().rstrip(";")

        parsed = sqlparse.parse(sql)
        if not parsed:
            return {"mongodb_query": "", "warnings": ["Unable to parse SQL"], "success": False}

        statement = parsed[0]
        upper_sql = sql.upper()

        if "JOIN" in upper_sql:
            self._warn("JOIN operations are not fully supported")
        if "HAVING" in upper_sql:
            self._warn("HAVING clause is not supported")
        if "UNION" in upper_sql:
            self._warn("UNION is not supported")
        if "INSERT" in upper_sql or "UPDATE" in upper_sql or "DELETE" in upper_sql:
            self._warn("Only SELECT queries are supported for translation")

        table = self._extract_table(statement)
        columns = self._extract_columns(statement)
        where_filter = self._extract_where(statement)
        order_by = self._extract_order_by(sql)
        limit = self._extract_limit(sql)
        group_by = self._extract_group_by(sql)

        if group_by:
            return self._build_aggregate(table, columns, where_filter, group_by)

        return self._build_find(table, columns, where_filter, order_by, limit)

    def _warn(self, message: str) -> None:
        logger.warning(message)
        self.UNSUPPORTED_WARNINGS.append(message)

    def _extract_table(self, statement) -> str:
        from_seen = False
        for token in statement.tokens:
            if from_seen:
                if isinstance(token, Identifier):
                    return token.get_real_name()
                if token.ttype is Name:
                    return str(token).strip()
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
        return "collection"

    def _extract_columns(self, statement) -> list[str]:
        columns = []
        select_seen = False
        for token in statement.tokens:
            if select_seen:
                if isinstance(token, IdentifierList):
                    for item in token.get_identifiers():
                        columns.append(self._col_name(item))
                    break
                if isinstance(token, Identifier):
                    columns.append(self._col_name(token))
                    break
                if token.ttype is Keyword and token.value.upper() == "FROM":
                    break
            if token.ttype is Keyword and token.value.upper() == "SELECT":
                select_seen = True

        if not columns or (len(columns) == 1 and columns[0] == "*"):
            return ["*"]
        return columns

    def _col_name(self, identifier) -> str:
        name = identifier.get_real_name() if hasattr(identifier, "get_real_name") else str(identifier)
        return name.strip()

    def _extract_where(self, statement) -> dict[str, Any]:
        filter_doc: dict[str, Any] = {}
        where_seen = False
        for token in statement.tokens:
            if where_seen:
                if isinstance(token, Comparison):
                    left, op, right = self._parse_comparison(token)
                    if left:
                        filter_doc.update(self._mongo_op(left, op, right))
                elif isinstance(token, Parenthesis):
                    inner = str(token).strip("()")
                    sub = self.translate(f"SELECT * FROM t WHERE {inner}")
                    if sub.get("filter"):
                        filter_doc.update(sub["filter"])
                elif token.ttype is Keyword:
                    break
            if token.ttype is Keyword and token.value.upper() == "WHERE":
                where_seen = True

        if not filter_doc:
            filter_doc = self._extract_where_regex(str(statement))
        return filter_doc

    def _extract_where_regex(self, sql: str) -> dict[str, Any]:
        """Fallback WHERE extraction using regex."""
        match = re.search(
            r"WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)",
            sql,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return {}

        clause = match.group(1).strip()
        filter_doc: dict[str, Any] = {}
        for part in re.split(r"\s+AND\s+", clause, flags=re.IGNORECASE):
            cm = re.match(
                r"(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*(.+)",
                part.strip(),
                re.IGNORECASE,
            )
            if cm:
                col, op, val = cm.group(1), cm.group(2), cm.group(3).strip().strip("'\"")
                filter_doc.update(self._mongo_op(col, op, val))
        return filter_doc

    def _parse_comparison(self, comparison: Comparison) -> tuple[str, str, str]:
        left = right = ""
        op = "="
        for token in comparison.tokens:
            if isinstance(token, Identifier):
                if not left:
                    left = token.get_real_name()
                else:
                    right = token.get_real_name()
            elif token.ttype is Token.Operator.Comparison:
                op = str(token).strip()
            elif token.ttype not in (Token.Text.Whitespace,):
                val = str(token).strip().strip("'\"")
                if val and val.upper() not in ("AND", "OR"):
                    right = val
        return left, op, right

    def _mongo_op(self, column: str, op: str, value: str) -> dict[str, Any]:
        """Convert SQL comparison to MongoDB operator."""
        ops_map = {
            "=": lambda v: v,
            "!=": lambda v: {"$ne": self._cast_value(v)},
            "<>": lambda v: {"$ne": self._cast_value(v)},
            ">": lambda v: {"$gt": self._cast_value(v)},
            "<": lambda v: {"$lt": self._cast_value(v)},
            ">=": lambda v: {"$gte": self._cast_value(v)},
            "<=": lambda v: {"$lte": self._cast_value(v)},
        }
        converter = ops_map.get(op, ops_map["="])
        result = converter(value)
        if isinstance(result, dict):
            return {column: result}
        return {column: result}

    def _cast_value(self, value: str) -> Any:
        value = value.strip().strip("'\"")
        if re.match(r"^-?\d+$", value):
            return int(value)
        if re.match(r"^-?\d+\.\d+$", value):
            return float(value)
        return value

    def _extract_order_by(self, sql: str) -> list[tuple[str, int]]:
        match = re.search(
            r"ORDER\s+BY\s+(.+?)(?:\s+LIMIT|\s*;?\s*$)",
            sql,
            re.IGNORECASE,
        )
        if not match:
            return []
        parts = match.group(1).split(",")
        order = []
        for part in parts:
            tokens = part.strip().split()
            col = tokens[0]
            direction = -1 if len(tokens) > 1 and tokens[1].upper() == "DESC" else 1
            order.append((col, direction))
        return order

    def _extract_limit(self, sql: str) -> int | None:
        match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_group_by(self, sql: str) -> list[str]:
        match = re.search(
            r"GROUP\s+BY\s+(.+?)(?:\s+HAVING|\s+ORDER\s+BY|\s+LIMIT|\s*;?\s*$)",
            sql,
            re.IGNORECASE,
        )
        if not match:
            return []
        return [c.strip() for c in match.group(1).split(",")]

    def _build_projection(self, columns: list[str]) -> dict[str, int]:
        if columns == ["*"]:
            return {}
        return {col: 1 for col in columns}

    def _format_doc(self, doc: dict) -> str:
        if not doc:
            return "{}"
        parts = []
        for k, v in doc.items():
            if isinstance(v, dict):
                inner = ", ".join(f"{ik}: {self._format_value(iv)}" for ik, iv in v.items())
                parts.append(f"{k}: {{ {inner} }}")
            else:
                parts.append(f"{k}: {self._format_value(v)}")
        return "{ " + ", ".join(parts) + " }"

    def _format_value(self, v: Any) -> str:
        if isinstance(v, str):
            return f'"{v}"'
        return str(v)

    def _build_find(
        self,
        table: str,
        columns: list[str],
        where_filter: dict,
        order_by: list[tuple[str, int]],
        limit: int | None,
    ) -> dict[str, Any]:
        projection = self._build_projection(columns)
        filter_str = self._format_doc(where_filter)
        proj_str = self._format_doc(projection) if projection else ""

        query = f"db.{table}.find(\n  {filter_str}"
        if proj_str:
            query += f",\n  {proj_str}"
        query += "\n)"

        if order_by:
            sort_doc = ", ".join(f'"{c}": {d}' for c, d in order_by)
            query += f".sort({{ {sort_doc} }})"
        if limit is not None:
            query += f".limit({limit})"

        return {
            "mongodb_query": query,
            "collection": table,
            "filter": where_filter,
            "projection": projection,
            "warnings": self.UNSUPPORTED_WARNINGS,
            "success": True,
        }

    def _build_aggregate(
        self,
        table: str,
        columns: list[str],
        where_filter: dict,
        group_by: list[str],
    ) -> dict[str, Any]:
        group_id = group_by[0] if len(group_by) == 1 else {c: f"${c}" for c in group_by}
        pipeline = []
        if where_filter:
            pipeline.append({"$match": where_filter})
        pipeline.append({"$group": {"_id": group_id}})

        import json

        pipeline_str = json.dumps(pipeline, indent=2)
        query = f"db.{table}.aggregate(\n{pipeline_str}\n)"

        return {
            "mongodb_query": query,
            "collection": table,
            "pipeline": pipeline,
            "warnings": self.UNSUPPORTED_WARNINGS,
            "success": True,
        }
