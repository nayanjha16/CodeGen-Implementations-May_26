"""Extract the query (and optional analysis) from model output (SPEC §6.1, plan §5).

The model emits either ``<marker> <query>`` (Stage A) or
``Analysis: <diagnosis> | <marker> <query>`` (Stage B), where marker is
``Corrected_SQL:`` (SQL) or ``Final_MQL:`` (MQL). Extraction splits on the
marker and **tolerates the ``Analysis:`` prefix being absent** — a Stage-A
generation has no analysis, and a Stage-B generation may drop it.

Queries in this data are single-line; cleaning stops at the first newline, at a
following section header (``###``), a second ``|`` separator, or an EOS token,
and strips code fences. An errored/empty extraction returns ``""`` — the harness
(``mongo_exec`` / Spider evaluator) treats that as a wrong query, the desired
signal, rather than raising.
"""

from __future__ import annotations

from . import config

_EOS = "<|endoftext|>"
_STOPS = ("###", _EOS)


def _clean_query(raw: str) -> str:
    """Reduce a raw post-marker span to a single clean query string."""
    q = raw.strip()
    # Drop anything from a following section header or EOS onward.
    for stop in _STOPS:
        idx = q.find(stop)
        if idx != -1:
            q = q[:idx]
    q = q.strip()
    if not q:
        return ""
    # Strip a leading ``` or ```lang fence line, then trailing fence.
    if q.startswith("```"):
        q = q.split("\n", 1)[1] if "\n" in q else ""
    q = q.strip()
    # Queries are single-line; keep the first non-empty line.
    for line in q.splitlines():
        line = line.strip()
        if line:
            q = line
            break
    return q.strip().strip("`").strip()


def extract(text: str, task: str) -> tuple[str | None, str]:
    """Return ``(analysis, query)`` from a model completion for ``task``.

    ``analysis`` is ``None`` when no ``Analysis:`` prefix is present. When the
    marker itself is missing, the whole text is treated as the query (best effort).
    """
    if task not in config.OUTPUT_MARKERS:
        raise ValueError(f"unknown task {task!r}")
    marker = config.OUTPUT_MARKERS[task]

    analysis: str | None = None
    if marker in text:
        before, after = text.split(marker, 1)
        if "Analysis:" in before:
            analysis = before.split("Analysis:", 1)[1].strip()
            # trailing " | " separator before the marker
            analysis = analysis.rstrip().rstrip("|").strip()
        query = after
    else:
        query = text

    return analysis, _clean_query(query)


def clean_generated_sql(text: str) -> str:
    """Extract just the SQL query from a text2sql completion."""
    return extract(text, "text2sql")[1]


def clean_generated_nosql(text: str, task: str = "text2nosql") -> str:
    """Extract just the MQL query from a NoSQL completion."""
    return extract(text, task)[1]
