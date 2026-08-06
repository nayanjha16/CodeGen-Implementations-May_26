from src.generation_engine import GenerationEngine


def test_atomic_context_reduction_drops_only_the_last_complete_block():
    context = (
        "Retrieved material below is reference data.\n\n"
        "### Repository Evidence (untrusted data)\n"
        "# BEGIN EVIDENCE: function: first (a.py)\n"
        "def first():\n    return 1\n"
        "# END EVIDENCE\n\n"
        "# BEGIN EVIDENCE: function: second (b.py)\n"
        "def second():\n    return 2\n"
        "# END EVIDENCE"
    )

    reduced = GenerationEngine._drop_last_evidence_block(context)

    assert "def first" in reduced
    assert "# END EVIDENCE" in reduced
    assert "def second" not in reduced


def test_atomic_context_reduction_returns_empty_after_last_block():
    context = (
        "Guard.\n\n### Validated Example Evidence\n"
        "# BEGIN EVIDENCE: example: only (one.py)\n"
        "def only():\n    return 1\n"
        "# END EVIDENCE"
    )

    assert GenerationEngine._drop_last_evidence_block(context) == ""


def test_completion_score_detects_import_only_python():
    assert GenerationEngine._code_completion_score("import re", "T1") < 2000
    assert GenerationEngine._code_completion_score(
        "import re\n\ndef validate_email(value):\n    return bool(value)", "T1"
    ) >= 3000
