from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def render_charts(csv_path: Path, out_dir: Path, metric: str = "ex") -> list[Path]:
    df = pd.read_csv(csv_path)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    by_model = df.groupby("model")[metric].mean()
    ax = by_model.plot(kind="bar", title=f"{metric} by model")
    ax.set_ylabel(metric)
    p1 = out_dir / f"{metric}_by_model.png"
    ax.figure.savefig(p1, bbox_inches="tight"); ax.figure.clf(); paths.append(p1)

    by_scn = df.groupby("scenario")[metric].mean()
    ax = by_scn.plot(kind="bar", title=f"{metric} by scenario")
    ax.set_ylabel(metric)
    p2 = out_dir / f"{metric}_by_scenario.png"
    ax.figure.savefig(p2, bbox_inches="tight"); ax.figure.clf(); paths.append(p2)

    pivot = df.pivot_table(index="model", columns="scenario", values=metric, aggfunc="mean")
    fig, ax = plt.subplots()
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
    ax.set_title(f"{metric}: model x scenario"); fig.colorbar(im)
    p3 = out_dir / f"{metric}_heatmap.png"
    fig.savefig(p3, bbox_inches="tight"); plt.close(fig); paths.append(p3)
    return paths
