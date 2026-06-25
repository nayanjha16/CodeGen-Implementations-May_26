"""Build prompts for SQL-to-MongoDB conversion."""

from __future__ import annotations

from typing import Any

from src.training.tasks import TaskType, format_task_prompt


class NoSQLPromptBuilder:
    """Build prompts for converting SQL queries to MongoDB shell syntax."""

    TEMPLATE = """Convert the SQL query into a MongoDB shell query.

Requirements:

* Return exactly one MongoDB shell query.
* Return only the query text.
* No explanations.
* No SQL.
* No markdown.
* No extra text.
* The response MUST start with: `db.`
* The response MUST contain exactly one MongoDB query.
* If the response does not start with `db.`, it is incorrect.

Example

SQL:
SELECT COUNT(*) FROM users

MongoDB:
db.users.countDocuments({{}})

MongoDB collections:
{mongodb_schema}

SQL:
{sql_query}

MongoDB:
"""

    def __init__(self, template: str | None = None):
        self.template = template or self.TEMPLATE

    @classmethod
    def for_model(cls, model_name: str, config: dict[str, Any] | None = None) -> "NoSQLPromptBuilder":
        """Create a prompt builder for the given model."""
        return cls()

    def build(
        self,
        sql_query: str,
        schema: str,
        nosql_schema: str | None = None,
    ) -> str:
        """Build a prompt from SQL query and MongoDB schema."""
        from src.utils.schema_conversion import derive_mongo_schema_json

        if nosql_schema is None:
            mongo_schema = derive_mongo_schema_json(schema.strip())
        else:
            mongo_schema = nosql_schema.strip() or "{}"

        prompt = self.template.format(
            mongodb_schema=mongo_schema,
            sql_query=sql_query.strip(),
        ).strip()
        return format_task_prompt(TaskType.SQL2NOSQL.value, prompt)

    def get_template_name(self) -> str:
        """Return template identifier for experiment tracking."""
        return "custom" if self.template != self.TEMPLATE else "default"
