import json
from pathlib import Path
from text2sql.report.writer import write_raw, aggregate_to_csv

def test_write_raw_creates_json(tmp_path):
    path = write_raw(tmp_path, model="m1", scenario="zero_shot", dataset="spider",
                     metrics={"ex": 0.5, "bleu": 42.0},
                     meta={"sample_size": 2}, per_example=[{"ex": 1}, {"ex": 0}])
    data = json.loads(Path(path).read_text())
    assert data["model"] == "m1"
    assert data["metrics"]["ex"] == 0.5
    assert len(data["per_example"]) == 2

def test_aggregate_to_csv_collects_all_raw(tmp_path):
    raw = tmp_path / "raw"; raw.mkdir()
    write_raw(raw, "m1", "zero_shot", "spider", {"ex": 0.5}, {}, [])
    write_raw(raw, "m1", "one_shot", "spider", {"ex": 0.7}, {}, [])
    csv_path = aggregate_to_csv(raw, tmp_path / "comparison.csv")
    text = Path(csv_path).read_text()
    assert "zero_shot" in text and "one_shot" in text
    assert text.count("\n") >= 3
