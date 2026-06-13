"""The single place the prompt format lives.

Both HFTranslator and the eval runner build prompts through here, so the
format seen at inference matches the format used during evaluation.
"""

from __future__ import annotations

from rustgen.translator.base import TranslationTask


def build_prompt(task: TranslationTask, examples: list[str]) -> str:
    """Retrieved examples as `// Example:` blocks, then the task block:
    doc-comment description, optional Python reference, optional signature."""
    parts = [f"// Example:\n{example.strip()}" for example in examples]

    lines = [f"/// {line}" for line in task.description.strip().splitlines()]
    if task.python_code:
        lines.append("// Python reference:")
        lines.extend(f"// {line}" for line in task.python_code.strip().splitlines())
    if task.signature:
        lines.append(task.signature.strip())
    parts.append("\n".join(lines))

    return "\n\n".join(parts)
