import json
from pathlib import Path
from text2sql.types import Example, SchemaInfo
from text2sql.schema.linker import SchemaLinker
from text2sql.schema.builder import SchemaBuilder
from text2sql.prompt.zero_shot import build_zero_shot_prompt

def build_finetune_jsonl(examples: list[Example], schemas: dict[str, SchemaInfo],
                         db_paths: dict, out_path: Path, sample_rows: int = 3) -> int:
    linker = SchemaLinker()
    builder = SchemaBuilder(sample_rows=sample_rows)
    out_path = Path(out_path)
    written = 0
    with out_path.open("w") as f:
        for ex in examples:
            schema = schemas[ex.db_id]
            tables = linker.link(ex.question, schema, ex.evidence)
            schema_str = builder.build(schema, tables, db_paths.get(ex.db_id))
            prompt = build_zero_shot_prompt(schema_str, ex.question, ex.evidence)
            f.write(json.dumps({"prompt": prompt, "completion": " " + ex.gold_sql}) + "\n")
            written += 1
    return written
