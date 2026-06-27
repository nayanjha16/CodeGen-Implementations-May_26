from pathlib import Path
from text2sql.config import load_config

def test_loads_models_and_scenarios(tmp_path):
    yaml_text = """
models:
  - id: qwen3-coder-32b
    mlx_repo: mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit
    hf_repo: Qwen/Qwen3-Coder-30B-A3B-Instruct
    backend: mlx
scenarios: [zero_shot, one_shot]
datasets: [spider]
evaluation:
  metrics: [ex, bleu]
  llm_judge_model: qwen3-coder-32b
  sample_size: 50
"""
    p = tmp_path / "config.yaml"; p.write_text(yaml_text)
    cfg = load_config(p)
    assert cfg.models[0]["id"] == "qwen3-coder-32b"
    assert cfg.scenarios == ["zero_shot", "one_shot"]
    assert cfg.evaluation["sample_size"] == 50

def test_expands_experiment_matrix(tmp_path):
    yaml_text = """
models:
  - {id: m1, mlx_repo: r, hf_repo: h, backend: mlx}
scenarios: [zero_shot, one_shot]
datasets: [spider, bird]
evaluation: {metrics: [ex], llm_judge_model: m1, sample_size: null}
"""
    p = tmp_path / "c.yaml"; p.write_text(yaml_text)
    cfg = load_config(p)
    matrix = cfg.experiments()
    assert len(matrix) == 4
    assert {"model": "m1", "scenario": "zero_shot", "dataset": "spider"} in matrix
