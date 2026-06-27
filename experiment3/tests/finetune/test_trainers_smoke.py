import json
import pytest

@pytest.mark.needs_model
def test_mlx_trainer_produces_adapter(tmp_path):
    from text2sql.finetune.mlx_trainer import MLXTrainer
    rows = [{"prompt": "### SQL:\n", "completion": " SELECT 1"} for _ in range(8)]
    train = tmp_path / "train.jsonl"; valid = tmp_path / "valid.jsonl"
    for p in (train, valid):
        p.write_text("\n".join(json.dumps(r) for r in rows))
    out = MLXTrainer("mlx-community/Qwen2.5-Coder-0.5B-Instruct-4bit", iters=2).train(train, valid, tmp_path / "adapter")
    assert out.exists()
