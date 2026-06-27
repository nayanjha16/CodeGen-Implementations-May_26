from pathlib import Path
import pandas as pd
from text2sql.report.charts import render_charts

def test_renders_png_files(tmp_path):
    df = pd.DataFrame([
        {"model": "m1", "scenario": "zero_shot", "dataset": "spider", "ex": 0.5},
        {"model": "m1", "scenario": "one_shot", "dataset": "spider", "ex": 0.7},
        {"model": "m2", "scenario": "zero_shot", "dataset": "spider", "ex": 0.4},
    ])
    csv = tmp_path / "c.csv"; df.to_csv(csv, index=False)
    out_dir = tmp_path / "charts"
    paths = render_charts(csv, out_dir, metric="ex")
    assert len(paths) >= 1
    assert all(Path(p).exists() and Path(p).suffix == ".png" for p in paths)
