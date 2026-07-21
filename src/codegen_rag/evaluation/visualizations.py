"""Research-quality comparison charts and a markdown results report.

matplotlib is imported lazily inside each function so the rest of the
evaluation package (and its tests) never need it installed just to be
imported — only the notebooks that actually render charts do.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def plot_bar_comparison(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    output_path: Path,
    title: str = "",
    ylabel: str = "",
) -> Path:
    """Generic labeled bar chart — used for the 4-tier and per-task comparisons."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df[category_col].astype(str), df[value_col], color="#3B6FA0")
    ax.set_title(title or f"{value_col} by {category_col}")
    ax.set_ylabel(ylabel or value_col)
    ax.set_xlabel(category_col)
    plt.xticks(rotation=30, ha="right")

    for bar, value in zip(bars, df[value_col], strict=True):
        if pd.notna(value):
            ax.annotate(
                f"{value:.3f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9,
            )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Saved chart to %s", output_path)
    return output_path


def plot_topk_sweep(topk_df: pd.DataFrame, output_path: Path, metric_col: str = "codebleu") -> Path:
    """Line chart of metric vs. K, one line per retrieval strategy — the
    visualization behind "evidence of the optimal top-K value"."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    numeric_df = topk_df[topk_df["dynamic"] == False]  # noqa: E712 - pandas boolean mask idiom

    for strategy, group in numeric_df.groupby("strategy"):
        group = group.sort_values("top_k")
        ax.plot(group["top_k"], group[metric_col], marker="o", label=strategy)

    ax.set_xlabel("Top-K")
    ax.set_ylabel(metric_col)
    ax.set_title("Retrieval strategy x Top-K sweep")
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Saved top-K sweep chart to %s", output_path)
    return output_path


def generate_markdown_report(
    sections: dict[str, Any],
    output_path: Path,
    title: str = "CodeGen Capstone — Evaluation Report",
) -> Path:
    """Render a set of {heading: content} sections (strings, DataFrames, or
    lists of chart paths) into a single markdown report."""
    lines = [f"# {title}\n"]

    for heading, content in sections.items():
        lines.append(f"## {heading}\n")
        if isinstance(content, pd.DataFrame):
            lines.append(content.to_markdown(index=False))
        elif isinstance(content, (list, tuple)) and content and isinstance(content[0], Path):
            for chart_path in content:
                lines.append(f"![{chart_path.stem}]({chart_path.name})")
        else:
            lines.append(str(content))
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote markdown report to %s", output_path)
    return output_path
