from text2sql.types import Example
from text2sql.prompt.zero_shot import _INSTRUCTION

def build_one_shot_prompt(schema_str: str, question: str, shot: Example, evidence: str = "") -> str:
    parts = [_INSTRUCTION, "",
             "### Example:",
             "Question: " + shot.question,
             "SQL: " + shot.gold_sql, "",
             "### Database schema:", schema_str]
    if evidence:
        parts += ["", "### Hint:", evidence]
    parts += ["", "### Question:", question, "", "### SQL:"]
    return "\n".join(parts)
