"""Build prompts for MongoDB query documentation generation."""

from __future__ import annotations

from typing import Any


class DocumentationPromptBuilder:
    """Build prompts that explain MongoDB shell queries in plain English."""

    TEMPLATE = """Generate documentation for the MongoDB shell query below.

Requirements:

* Explain what the query does in plain English.
* Mention the collection name and operation type (find, aggregate, distinct, or countDocuments).
* Describe filters, projections, sorting, limits, and aggregation stages when present.
* Return documentation text only.
* No code.
* No markdown fences.
* No extra headings or labels.

MongoDB collections:
{mongodb_schema}

MongoDB query:
{mongodb_query}

Documentation:
"""

    def __init__(self, template: str | None = None):
        self.template = template or self.TEMPLATE

    @classmethod
    def for_model(
        cls, model_name: str, config: dict[str, Any] | None = None
    ) -> "DocumentationPromptBuilder":
        """Create a prompt builder for the given model."""
        return cls()

    def build(
        self,
        mongodb_query: str,
        schema: str = "",
        nosql_schema: str | None = None,
    ) -> str:
        """Build a documentation prompt from a MongoDB query and schema."""
        from src.utils.schema_conversion import derive_mongo_schema_json

        if nosql_schema is None:
            mongo_schema = derive_mongo_schema_json(schema.strip()) if schema.strip() else "{}"
        else:
            mongo_schema = nosql_schema.strip() or "{}"

        return self.template.format(
            mongodb_schema=mongo_schema,
            mongodb_query=mongodb_query.strip(),
        ).strip()

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return "custom" if self.template != self.TEMPLATE else "default"
