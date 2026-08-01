"""Generate static PNG charts for docs/reference/lora-v1-v3-vs-baseline-comparison.pptx."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "reference" / "images" / "lora-v1-v3"

# Presentation palette — light / dark blue + neutral baseline
BLUE_DARK = "#1e40af"   # LoRA / primary series / best result
BLUE_MID = "#3b82f6"    # secondary emphasis
BLUE_LIGHT = "#93c5fd"  # baseline / alternate task
BLUE_PALE = "#dbeafe"   # baseline bars in paired charts
SLATE = "#64748b"       # neutral baseline
SLATE_LIGHT = "#cbd5e1"
TEXT = "#1e293b"
GRID = "#e2e8f0"

SERIES_COLORS = {
    "Text2SQL": BLUE_DARK,
    "SQL2NoSQL": BLUE_LIGHT,
    "Baseline v1": SLATE_LIGHT,
    "LoRA v1": BLUE_DARK,
}

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "#fafbfc",
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT,
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Calibri", "DejaVu Sans", "Arial"],
        "grid.color": GRID,
        "grid.linestyle": "--",
        "grid.linewidth": 0.8,
        "legend.fontsize": 10,
    }
)


def _save(fig: plt.Figure, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _style_bars(bars, color: str, edge: str = "#ffffff") -> None:
    for bar in bars:
        bar.set_color(color)
        bar.set_edgecolor(edge)
        bar.set_linewidth(0.8)


def _grouped_bar(
    categories: list[str],
    series: dict[str, list[float]],
    title: str,
    ylabel: str,
    filename: str,
    ylim: tuple[float, float] | None = None,
    value_suffix: str = "%",
    decimals: int = 0,
) -> Path:
    x = np.arange(len(categories))
    n = len(series)
    width = 0.8 / n
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    fallback = [BLUE_DARK, BLUE_LIGHT, BLUE_MID, SLATE]

    for i, (label, values) in enumerate(series.items()):
        offset = (i - (n - 1) / 2) * width
        color = SERIES_COLORS.get(label, fallback[i % len(fallback)])
        bars = ax.bar(x + offset, values, width, label=label, zorder=3)
        _style_bars(bars, color)
        for bar, val in zip(bars, values, strict=True):
            if val == 0 and "v1" in title.lower():
                continue
            fmt = f"{{:.{decimals}f}}{value_suffix}"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (ylim[1] if ylim else max(values) or 1) * 0.015,
                fmt.format(val),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=TEXT,
            )

    ax.set_title(title, pad=14, color=TEXT)
    ax.set_ylabel(ylabel, color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=12, ha="right")
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor=GRID)
    ax.yaxis.grid(True, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ylim:
        ax.set_ylim(*ylim)
    return _save(fig, filename)


def _single_bar(
    categories: list[str],
    values: list[float],
    colors: list[str],
    title: str,
    ylabel: str,
    filename: str,
    ylim: tuple[float, float],
    footnote: str | None = None,
    value_fmt: str = "{:.2f}",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(categories, values, width=0.58, zorder=3)
    for bar, color, val in zip(bars, colors, values, strict=True):
        bar.set_color(color)
        bar.set_edgecolor("#ffffff")
        bar.set_linewidth(0.8)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (ylim[1] - ylim[0]) * 0.02,
            value_fmt.format(val),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=TEXT,
        )
    ax.set_title(title, pad=14, color=TEXT)
    ax.set_ylabel(ylabel, color=TEXT)
    ax.set_ylim(*ylim)
    ax.yaxis.grid(True, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right")
    if footnote:
        ax.text(0.02, 0.02, footnote, transform=ax.transAxes, fontsize=8, color=SLATE)
    return _save(fig, filename)


def chart_improvement_execution() -> Path:
    cats = ["Baseline", "LoRA v1*", "LoRA v2", "LoRA v3"]
    return _grouped_bar(
        cats,
        {"Text2SQL": [14, 0, 60, 66], "SQL2NoSQL": [22.2, 0, 74, 86]},
        "Improvement — Execution Accuracy (Baseline → v1 → v2 → v3)",
        "Accuracy (%)",
        "00_improvement_execution_baseline_v1_v2_v3.png",
        ylim=(0, 95),
    )


def chart_improvement_exact_match() -> Path:
    cats = ["Baseline", "LoRA v1*", "LoRA v2", "LoRA v3"]
    return _grouped_bar(
        cats,
        {"Text2SQL": [0, 0, 40, 48], "SQL2NoSQL": [4, 0, 62, 78]},
        "Improvement — Exact Match (Baseline → v1 → v2 → v3)",
        "Exact match (%)",
        "00_improvement_exact_match_baseline_v1_v2_v3.png",
        ylim=(0, 85),
    )


def chart_improvement_doc_judge() -> Path:
    return _single_bar(
        ["Baseline", "LoRA v2", "LoRA v3"],
        [8.33, 8.41, 8.82],
        [SLATE_LIGHT, BLUE_MID, BLUE_DARK],
        "Improvement — Documentation Judge (Baseline → v2 → v3, n=50)",
        "Judge score (0–10)",
        "00_improvement_doc_judge_baseline_v2_v3.png",
        ylim=(0, 10),
        footnote="* v1 = n=5 smoke only. v2/v3 = full TEND ~8k; v2: r=16, 5 ep; v3: r=32+FFN, 10 ep",
    )


def chart_execution_baseline_vs_lora() -> Path:
    cats = ["v2 Baseline", "v2 LoRA", "v3 Baseline", "v3 LoRA"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(cats))
    text2sql = [12, 60, 14, 66]
    sql2nosql = [22, 74, 22, 86]
    width = 0.35
    b1 = ax.bar(x - width / 2, text2sql, width, label="Text2SQL", color=BLUE_DARK, edgecolor="white")
    b2 = ax.bar(x + width / 2, sql2nosql, width, label="SQL2NoSQL", color=BLUE_LIGHT, edgecolor="white")
    bar_colors = [SLATE_LIGHT, BLUE_DARK, SLATE_LIGHT, BLUE_DARK]
    for bars, vals in ((b1, text2sql), (b2, sql2nosql)):
        for bar, val in zip(bars, vals, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.2,
                f"{val:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=TEXT,
            )
    for i, cat in enumerate(cats):
        if "Baseline" in cat:
            b1[i].set_color(SLATE_LIGHT)
            b1[i].set_edgecolor(SLATE)
            b2[i].set_color(BLUE_PALE)
            b2[i].set_edgecolor(BLUE_MID)
        else:
            b1[i].set_color(BLUE_DARK)
            b2[i].set_color(BLUE_LIGHT)
            b2[i].set_edgecolor(BLUE_MID)
    ax.set_title("Execution Accuracy — Baseline vs LoRA by Version", pad=14, color=TEXT)
    ax.set_ylabel("Accuracy (%)", color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=12, ha="right")
    ax.set_ylim(0, 95)
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID)
    ax.yaxis.grid(True, alpha=0.85)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return _save(fig, "01_execution_accuracy_baseline_vs_lora.png")


def chart_exact_match_baseline_vs_lora() -> Path:
    cats = ["v2 Baseline", "v2 LoRA", "v3 Baseline", "v3 LoRA"]
    return _grouped_bar(
        cats,
        {"Text2SQL": [0, 40, 0, 48], "SQL2NoSQL": [4, 62, 4, 78]},
        "Exact Match — Baseline vs LoRA v2/v3",
        "Exact match (%)",
        "02_exact_match_baseline_vs_lora.png",
        ylim=(0, 85),
    )


def chart_doc_judge_baseline_vs_lora() -> Path:
    cats = ["v2 Baseline", "v2 LoRA", "v3 Baseline", "v3 LoRA"]
    colors = [SLATE_LIGHT, BLUE_MID, SLATE_LIGHT, BLUE_DARK]
    return _single_bar(
        cats,
        [6.47, 8.41, 8.33, 8.82],
        colors,
        "Documentation Judge Score (0–10)",
        "Judge score",
        "03_documentation_judge_baseline_vs_lora.png",
        ylim=(0, 10),
    )


def chart_lora_execution_progression() -> Path:
    cats = ["v1 (n=5)", "v2 (n=50)", "v3 (n=50)"]
    return _grouped_bar(
        cats,
        {"Text2SQL": [0, 60, 66], "SQL2NoSQL": [0, 74, 86]},
        "LoRA Execution Accuracy by Training Version",
        "Accuracy (%)",
        "04_lora_execution_progression.png",
        ylim=(0, 95),
    )


def chart_lora_doc_progression() -> Path:
    return _single_bar(
        ["v1 smoke*", "v2 LoRA", "v3 LoRA"],
        [10.0, 8.41, 8.82],
        [SLATE_LIGHT, BLUE_MID, BLUE_DARK],
        "LoRA Documentation Quality by Version",
        "Score / scaled rate",
        "05_lora_doc_progression.png",
        ylim=(0, 10.5),
        footnote="* v1: judge correct rate × 10; not comparable to n=50 judge score",
        value_fmt="{:.2f}",
    )


def chart_v1_smoke_judge() -> Path:
    cats = ["text2sql", "sql2nosql", "documentation"]
    return _grouped_bar(
        cats,
        {"Baseline v1": [0, 40, 20], "LoRA v1": [40, 100, 100]},
        "v1 Smoke — Judge Correct Rate",
        "Judge correct (%)",
        "06_v1_smoke_judge_correct_rate.png",
        ylim=(0, 105),
    )


def chart_baseline_vs_lora_lift_v3() -> Path:
    metrics = ["Text2SQL EX", "SQL2NoSQL EX", "Text2SQL EM", "SQL2NoSQL EM"]
    baseline = [14, 22.2, 0, 4]
    lora = [66, 86, 48, 78]
    x = np.arange(len(metrics))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11.5, 5.5))
    b1 = ax.bar(
        x - width / 2,
        baseline,
        width,
        label="Baseline v3",
        color=BLUE_PALE,
        edgecolor=BLUE_MID,
        linewidth=1.0,
        zorder=3,
    )
    b2 = ax.bar(
        x + width / 2,
        lora,
        width,
        label="LoRA v3",
        color=BLUE_DARK,
        edgecolor="#ffffff",
        linewidth=0.8,
        zorder=3,
    )
    for bars, vals in ((b1, baseline), (b2, lora)):
        for bar, val in zip(bars, vals, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=TEXT,
            )
    ax.set_title("LoRA v3 vs Baseline v3 — Primary Metrics (n=50)", pad=14, color=TEXT)
    ax.set_ylabel("Score / accuracy (%)", color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 95)
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID)
    ax.yaxis.grid(True, alpha=0.85)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return _save(fig, "07_v3_baseline_vs_lora_summary.png")


def main() -> None:
    paths = [
        chart_improvement_execution(),
        chart_improvement_exact_match(),
        chart_improvement_doc_judge(),
        chart_execution_baseline_vs_lora(),
        chart_exact_match_baseline_vs_lora(),
        chart_doc_judge_baseline_vs_lora(),
        chart_lora_execution_progression(),
        chart_lora_doc_progression(),
        chart_v1_smoke_judge(),
        chart_baseline_vs_lora_lift_v3(),
    ]
    print(f"Wrote {len(paths)} charts to {OUT}")
    for p in paths:
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
