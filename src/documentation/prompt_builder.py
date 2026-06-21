"""Build prompts for MongoDB query documentation generation."""

from __future__ import annotations

from typing import Any


class DocumentationPromptBuilder:
    """Build prompts that explain MongoDB shell queries in plain English."""

    TEMPLATE = """You are an expert MongoDB documentation generator.

Generate concise, human-readable documentation for the MongoDB shell query.

Goal:
Explain what information the query retrieves, calculates, or summarizes—not how the MongoDB syntax works.

Instructions:

* Describe the query result in plain English.
* Mention the collection name and operation type.
* Explain the business meaning of filters, joins, aggregations, calculations, grouping, sorting, projections, limits, and distinct selections when present.
* For aggregation pipelines, describe the purpose of each important stage only if it affects the final result.
* When a natural language question is provided, generate documentation that directly answers that question.
* Infer intent from the query structure rather than repeating MongoDB operators.
* Use natural language field names where possible.
* Focus on the final output returned to the user.
* Do not explain MongoDB syntax.
* Do not mention operators such as $match, $group, $project, $sort, $lookup, etc.
* Do not include code, JSON, markdown, headings, labels, or bullet points.

Output Requirements:

* 1–3 concise sentences.
* Maximum 300 characters preferred.
* Documentation text only.

{question_section}MongoDB Schema:
{mongodb_schema}

MongoDB Query:
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
        question: str = "",
    ) -> str:
        """Build a documentation prompt from a MongoDB query, schema, and question."""
        from src.utils.schema_conversion import derive_mongo_schema_json

        if nosql_schema is None:
            mongo_schema = derive_mongo_schema_json(schema.strip()) if schema.strip() else "{}"
        else:
            mongo_schema = nosql_schema.strip() or "{}"

        question_text = question.strip()
        question_section = ""
        if question_text:
            question_section = (
                "Natural language question:\n"
                f"{question_text}\n\n"
            )

        return self.template.format(
            question_section=question_section,
            mongodb_schema=mongo_schema,
            mongodb_query=mongodb_query.strip(),
        ).strip()

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return "custom" if self.template != self.TEMPLATE else "default"
