import json
from pathlib import Path
import pandas as pd

def write_raw(raw_dir: Path, model: str, scenario: str, dataset: str,
              metrics: dict, meta: dict, per_example: list) -> Path:
    raw_dir = Path(raw_dir); raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "scenario": scenario, "dataset": dataset,
               "metrics": metrics, "meta": meta, "per_example": per_example}
    out = raw_dir / f"{model}_{scenario}_{dataset}.json"
    out.write_text(json.dumps(payload, indent=2))
    return out

def aggregate_to_csv(raw_dir: Path, csv_path: Path) -> Path:
    rows = []
    for f in sorted(Path(raw_dir).glob("*.json")):
        d = json.loads(f.read_text())
        row = {"model": d["model"], "scenario": d["scenario"], "dataset": d["dataset"]}
        row.update(d["metrics"])
        rows.append(row)
    df = pd.DataFrame(rows)
    csv_path = Path(csv_path); csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path
