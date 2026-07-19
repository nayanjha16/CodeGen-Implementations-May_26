"""Prompt helpers for multi-adapter generation."""

from __future__ import annotations

from codegen_api import INTENTS

CLARIFY_MESSAGE = (
    "I could not determine which task you want. Please ask for one of:\n"
    "- write / generate a SQL query (text -> SQL)\n"
    "- convert SQL to MongoDB / NoSQL\n"
    "- generate documentation for a MongoDB / NoSQL query\n"
    "Include the relevant schema in your prompt."
)


def format_generation_prompt(intent: str, user_content: str) -> str:
    """Prefix the user prompt with the LoRA task tag used in training.

    The caller is expected to include schema (and question / SQL / etc.)
    inside ``user_content``. If the content already starts with a ``Task:``
    tag, it is returned unchanged.
    """
    normalized = intent.strip().lower()
    if normalized not in INTENTS:
        raise ValueError(
            f"Unknown intent '{intent}'. Expected one of: {', '.join(INTENTS)}"
        )

    body = user_content.lstrip()
    if body.lower().startswith("task: "):
        return body
    return f"Task: {normalized}\n\n{body}"
