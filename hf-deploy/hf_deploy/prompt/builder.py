"""Prompt helpers for multi-adapter generation."""

from __future__ import annotations

from hf_deploy import INTENTS


def format_generation_prompt(intent: str, user_content: str) -> str:
    """Prefix the user prompt with the LoRA task tag used in training.

    Basic version: the caller already includes schema (and question/SQL/etc.)
    inside ``user_content``.
    """
    normalized = intent.strip().lower()
    if normalized not in INTENTS:
        raise ValueError(f"Unknown intent '{intent}'. Expected one of: {INTENTS}")
    body = user_content.lstrip()
    if body.lower().startswith(f"task: {normalized}"):
        return body
    return f"Task: {normalized}\n\n{body}"


CLARIFY_MESSAGE = (
    "I could not determine which task you want. Please ask for one of:\n"
    "- write / generate a SQL query (text → SQL)\n"
    "- convert SQL to MongoDB / NoSQL\n"
    "- generate documentation for a MongoDB / NoSQL query\n"
    "Include the relevant schema in your prompt."
)
