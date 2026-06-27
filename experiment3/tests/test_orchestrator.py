from pathlib import Path
from text2sql.models.base import StubRunner
from text2sql.orchestrator import run_single

FIX = Path(__file__).parent / "data" / "fixtures"

def test_run_single_writes_results(tmp_path):
    out = run_single(
        model_id="stub", scenario="zero_shot", dataset="spider",
        spider_root=FIX / "spider_mini", bird_root=FIX / "bird_mini",
        results_dir=tmp_path, metrics=["ex", "bleu"], sample_size=None,
        runner=StubRunner(responses=["SELECT count(*) FROM singer"]),
        retriever=None, judge_runner=None)
    assert Path(out).exists()
    import json
    data = json.loads(Path(out).read_text())
    assert data["metrics"]["ex"] == 1.0
    assert data["model"] == "stub"
