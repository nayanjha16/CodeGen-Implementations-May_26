"""Two-stage prompt construction for all three tasks (plan §5, SPEC §6.1).

Stage A (drafting) has no ``Broken Draft:`` line and targets the query marker
only (``Corrected_SQL:`` / ``Final_MQL:``). Stage B (revising) includes a
``Broken Draft:`` line and targets ``Analysis: … | <marker> <query>``.

Rules enforced here (plan §5 "Rules"):
- the ``### REFERENCE EXAMPLE ###`` block is omitted *entirely* when no reference
  is supplied — never rendered as the string ``"None"``;
- the ``Broken Draft:`` line is omitted *entirely* when there is no draft.

``build_prompt`` and ``build_target`` are separate so the trainer can tokenize
the prompt alone to find the loss-mask boundary (completion-only loss, plan §3).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config
from .loader import Example

REFERENCE_RULE = "#########################"


@dataclass(frozen=True)
class TaskLabels:
    input_label: str  # target-task input line label
    ref_input_label: str  # reference-example input line label
    ref_target_label: str  # reference-example target line label


# Input for sql2nosql is a SQL string, not an NL question — so its line labels
# differ. plan §5 illustrates only text2sql ("Question:"); these keep every task
# grounded in what its input actually is (see DECISIONS.md).
LABELS: dict[str, TaskLabels] = {
    "text2sql": TaskLabels("Question", "Context Question", "Target SQL"),
    "sql2nosql": TaskLabels("SQL", "Context SQL", "Target MQL"),
    "text2nosql": TaskLabels("Question", "Context Question", "Target MQL"),
}


def input_value(example: Example) -> str:
    """The task input string: source SQL for sql2nosql, else the NL question."""
    if example.task == "sql2nosql":
        return example.source_sql or ""
    return example.question or ""


def build_prompt(
    example: Example,
    reference: Example | None = None,
    broken_draft: str | None = None,
) -> str:
    """Construct the prompt up to and including ``### SYSTEM RESPONSE ###``.

    ``reference`` is a retrieved solved example (its input + gold). Passing
    ``broken_draft`` switches this from a Stage-A to a Stage-B prompt.
    """
    labels = LABELS[example.task]
    lines: list[str] = [config.TASK_HEADERS[example.task]]

    if reference is not None:
        lines += [
            "### REFERENCE EXAMPLE ###",
            f"{labels.ref_input_label}: {input_value(reference)}",
            f"{labels.ref_target_label}: {reference.gold}",
            REFERENCE_RULE,
            "",
        ]

    lines += [
        "### TARGET TASK ###",
        f"{labels.input_label}: {input_value(example)}",
        f"Schema: {example.schema}",
    ]
    if broken_draft is not None:
        lines.append(f"Broken Draft: {broken_draft}")

    lines += ["", "### SYSTEM RESPONSE ###"]
    return "\n".join(lines) + "\n"


def build_target(example: Example, analysis: str | None = None) -> str:
    """The completion the model must produce.

    Stage A (``analysis is None``): ``<marker> <gold>``.
    Stage B (analysis given): ``Analysis: <analysis> | <marker> <gold>``.
    """
    marker = config.OUTPUT_MARKERS[example.task]
    core = f"{marker} {example.gold}"
    if analysis is None:
        return core
    return f"Analysis: {analysis} | {core}"


def build_training_text(
    example: Example,
    reference: Example | None = None,
    broken_draft: str | None = None,
    analysis: str | None = None,
) -> tuple[str, str]:
    """Return ``(prompt, full_text)`` for training.

    ``full_text = prompt + target``. The trainer masks the prompt span so loss is
    computed on the target only (plan §3); returning both lets it find the split.
    """
    prompt = build_prompt(example, reference=reference, broken_draft=broken_draft)
    target = build_target(example, analysis=analysis)
    return prompt, prompt + target
