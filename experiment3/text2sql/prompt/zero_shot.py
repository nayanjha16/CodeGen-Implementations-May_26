_INSTRUCTION = (
    "You are an expert SQL developer. Given a database schema and a question, "
    "write a single valid SQLite SQL query that answers it. "
    "Return only the SQL query, no explanation."
)

def build_zero_shot_prompt(schema_str: str, question: str, evidence: str = "") -> str:
    parts = [_INSTRUCTION, "", "### Database schema:", schema_str]
    if evidence:
        parts += ["", "### Hint:", evidence]
    parts += ["", "### Question:", question, "", "### SQL:"]
    return "\n".join(parts)
