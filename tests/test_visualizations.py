from __future__ import annotations

from pathlib import Path

import pandas as pd

from codegen_rag.evaluation.visualizations import (
    generate_markdown_report,
    plot_bar_comparison,
    plot_topk_sweep,
)


def test_plot_bar_comparison_writes_png(tmp_path: Path):
    df = pd.DataFrame(
        [
            {"model_tier": "small_lm_baseline", "codebleu": 0.4},
            {"model_tier": "llm_no_rag", "codebleu": 0.65},
            {"model_tier": "llm_rag", "codebleu": 0.72},
        ]
    )
    out = tmp_path / "chart.png"
    result = plot_bar_comparison(df, "model_tier", "codebleu", out, title="4-tier comparison")
    assert result.exists()
    assert result.stat().st_size > 0


def test_plot_topk_sweep_writes_png(tmp_path: Path):
    df = pd.DataFrame(
        [
            {"strategy": "dense", "top_k": 1, "dynamic": False, "codebleu": 0.5},
            {"strategy": "dense", "top_k": 3, "dynamic": False, "codebleu": 0.6},
            {"strategy": "dense", "top_k": 5, "dynamic": False, "codebleu": 0.55},
            {"strategy": "hybrid", "top_k": 1, "dynamic": False, "codebleu": 0.52},
            {"strategy": "hybrid", "top_k": 3, "dynamic": False, "codebleu": 0.68},
            {"strategy": "hybrid", "top_k": 5, "dynamic": False, "codebleu": 0.7},
        ]
    )
    out = tmp_path / "topk.png"
    result = plot_topk_sweep(df, out)
    assert result.exists()
    assert result.stat().st_size > 0


def test_generate_markdown_report_includes_dataframe_and_text(tmp_path: Path):
    df = pd.DataFrame([{"task": "sql_generation", "execution_accuracy": 0.42}])
    out = tmp_path / "report.md"
    result = generate_markdown_report(
        {"Summary": "Overall the RAG pipeline improved results.", "SQL Results": df}, out
    )
    text = result.read_text()
    assert "Summary" in text
    assert "Overall the RAG pipeline improved results." in text
    assert "execution_accuracy" in text
    assert "sql_generation" in text
