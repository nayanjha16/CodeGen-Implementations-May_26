import json
from pathlib import Path
from text2sql.finetune.mlx_trainer import MLXTrainer

def _mk(p, rows):
    p.write_text("\n".join(json.dumps(r) for r in rows))

def test_text_format_converts_prompt_completion(tmp_path):
    src = tmp_path / "train.jsonl"; dst = tmp_path / "out.jsonl"
    _mk(src, [{"prompt": "Q: hi\nSQL:", "completion": " SELECT 1"}])
    MLXTrainer("repo", text_format=True)._write_data(src, dst)
    row = json.loads(dst.read_text().strip())
    assert row == {"text": "Q: hi\nSQL: SELECT 1"}  # concatenated, no chat template

def test_default_copies_prompt_completion_verbatim(tmp_path):
    src = tmp_path / "train.jsonl"; dst = tmp_path / "out.jsonl"
    rows = [{"prompt": "p", "completion": " c"}]
    _mk(src, rows)
    MLXTrainer("repo")._write_data(src, dst)  # text_format defaults False
    assert json.loads(dst.read_text().strip()) == rows[0]
