"""Deterministic mock backend so the UI and eval pipeline run with zero deps."""

from __future__ import annotations

from rustgen.translator.base import TranslationTask, Translator

_BODY = "fn add(a: i64, b: i64) -> i64 {\n    a + b\n}"


class MockTranslator(Translator):
    """Returns a fixed, compilable Rust function with the task echoed as docs."""

    def generate(self, task: TranslationTask) -> str:
        description = task.description.strip() or "(no description)"
        lines = [f"/// {line}" for line in description.splitlines()]
        mode = "Python -> Rust" if task.python_code is not None else "English -> Rust"
        lines.append(f"/// (mock backend, {mode} mode)")
        lines.append(_BODY)
        return "\n".join(lines) + "\n"
