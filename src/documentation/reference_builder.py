"""Rule-based reference documentation for MongoDB shell queries."""

from __future__ import annotations

import re
from typing import Any


_COLLECTION_RE = re.compile(
    r"db\.(\w+)\.(find|aggregate|distinct|countDocuments)\s*\(",
    re.IGNORECASE,
)


class ReferenceDocumentationBuilder:
    """Build deterministic reference documentation from MongoDB shell syntax."""

    def build(self, mongodb_query: str) -> str:
        """Return plain-English documentation for a MongoDB query."""
        query = mongodb_query.strip()
        if not query:
            return ""

        match = _COLLECTION_RE.search(query)
        if not match:
            return "This MongoDB query could not be parsed for documentation."

        collection = match.group(1)
        operation = match.group(2).lower()
        parts = [f"This query targets the `{collection}` collection."]

        if operation == "find":
            parts.append("It uses a find operation to retrieve matching documents.")
            if ".sort(" in query:
                parts.append("Results are sorted before being returned.")
            if ".limit(" in query:
                parts.append("The result set is limited to a maximum number of documents.")
        elif operation == "aggregate":
            parts.append("It uses an aggregation pipeline to compute grouped or transformed results.")
            if "$match" in query:
                parts.append("Documents are filtered before aggregation stages run.")
            if "$group" in query:
                parts.append("Documents are grouped to produce aggregate values.")
            if "$sort" in query:
                parts.append("Pipeline output is sorted.")
            if "$limit" in query:
                parts.append("The pipeline output is limited.")
        elif operation == "distinct":
            parts.append("It returns distinct values for the requested field.")
        elif operation == "countDocuments":
            parts.append("It counts documents that match the provided filter.")

        return " ".join(parts)

    def build_batch(self, queries: list[str]) -> list[str]:
        """Build reference documentation for multiple queries."""
        return [self.build(query) for query in queries]

    def to_structured(self, mongodb_query: str) -> dict[str, Any]:
        """Return parsed query metadata used by the evaluator."""
        query = mongodb_query.strip()
        match = _COLLECTION_RE.search(query)
        if not match:
            return {
                "collection": "",
                "operation": "",
                "valid": False,
            }
        return {
            "collection": match.group(1),
            "operation": match.group(2).lower(),
            "valid": True,
        }
