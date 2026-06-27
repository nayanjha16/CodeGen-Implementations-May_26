import json
from pathlib import Path
from text2sql.types import Example, SchemaInfo
from text2sql.finetune.dataset import build_finetune_jsonl

def test_writes_prompt_completion_jsonl(tmp_path):
    examples = [Example("db", "How many singers?", "SELECT count(*) FROM singer")]
    schemas = {"db": SchemaInfo(db_id="db", tables={"singer": ["singer_id", "name"]})}
    out = tmp_path / "train.jsonl"
    n = build_finetune_jsonl(examples, schemas, db_paths={"db": None}, out_path=out)
    assert n == 1
    row = json.loads(out.read_text().splitlines()[0])
    assert "singer" in row["prompt"]
    assert row["completion"].strip() == "SELECT count(*) FROM singer"
