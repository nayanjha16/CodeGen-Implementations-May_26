"""The single place the prompt format lives.

Both HFTranslator and the eval runner build prompts through here, so the
format seen at inference matches the format used during evaluation — and,
critically, the format the Step 3b translation fine-tune was trained on:

    // Reference Python implementation:
    // <python line 1>
    // ...
    /// <English description>
    fn <signature> {

Retrieved RAG examples are prepended as whole blocks in that same shape
(the corpus builder emits them pre-formatted), separated by blank lines.
"""

from __future__ import annotations

from rustgen.translator.base import TranslationTask


def python_as_comment(python_code: str) -> str:
    """Render Python source exactly the way the fine-tune saw it in training."""
    if not python_code:
        return ""
    lines = "\n".join("// " + line for line in python_code.strip().splitlines())
    return "// Reference Python implementation:\n" + lines + "\n"


def normalize_signature(signature: str) -> str:
    """`fn add(a: i64, b: i64) -> i64` -> `fn add(a: i64, b: i64) -> i64 {`."""
    sig = signature.strip()
    return sig if sig.endswith("{") else sig + " {"


def retrieval_query(task: TranslationTask) -> str:
    """What the retriever sees for a task: `///` doc comment + signature.

    This is the query shape the Step 6 sweep measured — at completion time the
    model has no Python, so retrieval must live with the same information. The
    completion-style corpus indexes each exemplar's doc comment + signature to
    match (see build_corpus).
    """
    lines = [f"/// {line}" for line in task.description.strip().splitlines()]
    if task.signature:
        lines.append(normalize_signature(task.signature))
    return "\n".join(lines) + "\n"


def build_prompt(task: TranslationTask, examples: list[str]) -> str:
    """Example blocks first, then: Python-as-comment, `///` description, signature."""
    parts = [example.strip() for example in examples]

    block = ""
    if task.python_code:
        block += python_as_comment(task.python_code)
    block += "\n".join(f"/// {line}" for line in task.description.strip().splitlines()) + "\n"
    if task.signature:
        block += normalize_signature(task.signature) + "\n"
    parts.append(block)

    return "\n\n".join(parts)
