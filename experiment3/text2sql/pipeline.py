from text2sql.types import Example, SchemaInfo, GenResult
from text2sql.schema.linker import SchemaLinker
from text2sql.schema.builder import SchemaBuilder
from text2sql.prompt.zero_shot import build_zero_shot_prompt
from text2sql.prompt.one_shot import build_one_shot_prompt
from text2sql.postprocess import extract_sql

def generate_for_examples(examples: list[Example], schemas: dict[str, SchemaInfo],
                          db_paths: dict, runner, scenario: str, retriever=None,
                          sample_rows: int = 3) -> list[GenResult]:
    linker = SchemaLinker()
    builder = SchemaBuilder(sample_rows=sample_rows)
    results: list[GenResult] = []
    for ex in examples:
        schema = schemas[ex.db_id]
        tables = linker.link(ex.question, schema, ex.evidence)
        schema_str = builder.build(schema, tables, db_paths.get(ex.db_id))
        if scenario == "one_shot":
            if retriever is None:
                raise ValueError("one_shot scenario requires a retriever")
            shot = retriever.retrieve(ex.question)
            prompt = build_one_shot_prompt(schema_str, ex.question, shot, ex.evidence)
        else:
            prompt = build_zero_shot_prompt(schema_str, ex.question, ex.evidence)
        raw = runner.generate(prompt)
        results.append(GenResult(example=ex, raw_output=raw, sql=extract_sql(raw)))
    return results
