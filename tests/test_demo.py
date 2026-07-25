"""Cascade wiring in the demo app, exercised against the mock backend —
no model weights, no network. Verifies the Step 6 attempt plan end to end:
K=0 first, then idiom + k=2, then k=4, gated only on compile success."""

import pytest

pytest.importorskip("gradio")
pytest.importorskip("sklearn")

from rustgen.app import demo  # noqa: E402  (import needs the skips above)


def _translate(use_cascade=True):
    return demo.translate(
        "Add two integers.",
        "def add(a, b):\n    return a + b",
        "fn add(a: i64, b: i64) -> i64",
        use_pivot=False, draft_sig=False, gen_tests=False,
        use_cascade=use_cascade)


def test_cascade_recovers_on_second_attempt(monkeypatch):
    # First attempt fails to compile, second succeeds -> the idiom + k=2
    # attempt must run, win, and be visible in the pipeline trail.
    verdicts = iter([False, True])
    monkeypatch.setattr(demo, "_quick_compiles", lambda code: next(verdicts))
    monkeypatch.setattr(demo, "verify_compiles", lambda code, tests=None: "✓ compiles (rustc)")

    pipeline, rust, *_ = _translate()
    assert "❌ RAG off" in pipeline
    assert "✅ idiom + k=2" in pipeline
    assert "k=4" not in pipeline          # cascade stops at first success
    assert rust.strip()


def test_cascade_attempts_include_the_idiom_exemplar(monkeypatch):
    # The retrieved-examples panel for the fallback attempt must contain the
    # idiom exemplar on top of the k=2 retrieved examples.
    verdicts = iter([False, True])
    monkeypatch.setattr(demo, "_quick_compiles", lambda code: next(verdicts))
    monkeypatch.setattr(demo, "verify_compiles", lambda code, tests=None: "✓ compiles (rustc)")

    out = _translate()
    retrieved_panel = out[4]
    assert "attempt idiom + k=2" in retrieved_panel
    idiom_signatures = ("element_at", "max_float", "sort_floats", "digit_sum_is_prime",
                        "average", "product_wide", "same_word", "char_at",
                        "value_range", "negative_positions")
    assert any(sig in retrieved_panel for sig in idiom_signatures)


def test_cascade_off_is_a_single_attempt(monkeypatch):
    calls = []
    monkeypatch.setattr(demo, "_quick_compiles", lambda code: calls.append(1) or False)
    monkeypatch.setattr(demo, "verify_compiles", lambda code, tests=None: "✗ compile failed")

    pipeline, *_ = _translate(use_cascade=False)
    assert len(calls) == 1
    assert "cascade" not in pipeline.lower()
