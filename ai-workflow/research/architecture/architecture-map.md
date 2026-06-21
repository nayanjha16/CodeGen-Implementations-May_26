# Architecture Map — CodeGen Studio (PEFT / LoRA Research)

> Current architecture as of 2026-06-21, oriented toward adding LoRA PEFT for the three
> tasks: **text2sql**, **sql2nosql**, **nosql2doc**.

## 1. Module Overview

| Package | Module | Responsibility |
|---------|--------|----------------|
| `src.models` | `model_loader.py` | `CodeGenModel` HF wrapper; `load_model()`; `ensure_model_cached()`; `resolve_model_path()` (checkpoint > base); `is_seq2seq_model()`. Lazy load, device resolve, greedy/beam, stop-strings. |
| `src.text2sql` | `prompt_builder.py` | `PromptBuilder` — schema+question → SQL prompt (`SQL:` suffix). |
| | `sql_generator.py` | `SQLGenerator` — model + prompt → SQL; multi-line extraction; stop strings. |
| | `sql_validator.py` / `sql_executor.py` | sqlparse + SQLite EXPLAIN validation; SQLite execution + result comparison. |
| `src.sql2nosql` | `prompt_builder.py` | `NoSQLPromptBuilder` — SQL + Mongo schema → Mongo-query prompt. |
| | `nosql_generator.py` | `NoSQLGenerator` — model → MongoDB shell query; `_parse_collection`. |
| | `translator.py` | `SQLToNoSQLTranslator` — rule-based SQL→Mongo (reference/gold path). |
| | `evaluator.py` | `NoSQLEvaluator` — query-level metrics + structural equivalence. |
| `src.documentation` | `prompt_builder.py` | `DocumentationPromptBuilder` — Mongo query+schema+question → doc prompt. |
| | `doc_generator.py` | `DocumentationGenerator` — model → plain-English doc; heavy output sanitizing; reference fallback. |
| | `evaluator.py` / `reference_builder.py` | `DocumentationEvaluator` (structure + text metrics); `ReferenceDocumentationBuilder` (rule-based reference doc). |
| `src.evaluation` | `metrics.py` | `EvaluationMetrics` — EM, exec acc, syntax, BLEU, ROUGE-L, BERTScore, CodeBLEU, token-F1. |
| | `benchmark.py` | `BenchmarkRunner` — runs all 3 tasks; logs to MLflow. |
| | `mlflow_tracker.py` / `qwen_evaluator.py` | MLflow logging; Qwen LLM-as-judge. |
| `src.datasets` | `spider_loader.py` / `bird_loader.py` | Download + standardize `{question, schema, sql, db_id}`. |
| | `preprocess.py` | Cleaning, splitting, statistics. |
| `src.utils` | `config.py`, `device.py`, `paths.py`, `seeds.py`, `logging.py`, `schema_conversion.py` | Config/`.env`, device resolve, model/data/checkpoint paths, seeds, logging, `derive_mongo_schema_json`. |
| `TEND` | `build_tend_dataset.py` | `TENDDatasetBuilder` — Spider → CSV with all task columns + doc + judge. |
| | `run_tend.py` / `scripts/run_all_tend.py` | CLI to generate train/validation CSVs. |
| | `qwen_doc_generator.py` / `qwen_evaluator.py` | Qwen documentation + semantic judge. |

## 2. Dependency Graph (import direction)

```
            configs/default.yaml + .env
                      |
                src.utils.config / paths / device
                      |
            +---------+-----------------------------+
            |                                        |
      src.models.model_loader            src.utils.schema_conversion
            |                                        |
   +--------+-----------+--------------------+       |
   |                    |                    |       |
src.text2sql       src.sql2nosql       src.documentation
 (PromptBuilder,    (NoSQLPrompt,       (DocPrompt,
  SQLGenerator)      NoSQLGenerator,     DocGenerator,
                     translator)         evaluator)
   \                    |                    /
    \                   |                   /
     +-----> src.evaluation.benchmark.BenchmarkRunner <-----+
                      |                |
            src.evaluation.metrics    src.evaluation.mlflow_tracker
                      ^
                      |
        src.datasets.spider_loader / bird_loader

TEND.build_tend_dataset --> src.sql2nosql.translator, src.utils.schema_conversion,
                            TEND.qwen_doc_generator, TEND.qwen_evaluator
                          --> data/TEND/*.csv  (the LoRA training source)
```

Key properties:
- **No circular imports.** Heavy deps (`torch`, `transformers`, metric libs) imported at
  call time.
- **DI throughout** — generators/benchmark accept injected collaborators (easy to add a
  trainer that reuses prompt builders).
- **Config + `.env` flow down**; `MODEL_NAME` and all paths come from `.env`.

## 3. The Three Tasks — Data Contract

The TEND CSV is the single supervised source. Each task maps columns to `(input, target)`
and **must reuse the existing prompt builder** so train-time and eval-time prompts match.

| Task | Prompt builder | Input columns | Target column |
|------|----------------|---------------|---------------|
| **text2sql** | `src.text2sql.PromptBuilder.build(question, schema)` | `question`, `sql_schema` | `sql_query` |
| **sql2nosql** | `src.sql2nosql.NoSQLPromptBuilder.build(sql_query, schema, nosql_schema)` | `sql_query`, `nosql_schema` | `nosql_query` |
| **nosql2doc** | `src.documentation.DocumentationPromptBuilder.build(mongodb_query, schema, nosql_schema, question)` | `nosql_query`, `nosql_schema`, `question` | `documentation` |

CSV columns present: `source, db_id, question, sql_schema, sql_query, nosql_schema,
nosql_query, documentation, metadata, conversion_success, schema_correct, query_correct,
overall_correct, schema_reason, query_reason, evaluation_response`.

## 4. Where LoRA Plugs In (proposed integration points)

```
data/TEND/*.csv
      │  (new) TEND→SFT dataset builder: row -> {"prompt": builder.build(...),
      │                                          "target": row[target_col]}
      ▼
(new) src.training.dataset  ── tokenize: prompt + target, mask prompt tokens in labels
      │
      ▼
(new) src.training.lora_trainer  ── peft.LoraConfig + get_peft_model(base)
      │                              Trainer / SFTTrainer; per-task adapter
      ▼
models/checkpoints/<task>_<model>_lora/   (adapter_config.json + adapter_model.safetensors)
      │
      ▼
src.models.model_loader.CodeGenModel.load()  ── (new) if adapter present:
      │   PeftModel.from_pretrained(base, adapter_dir)  [or merge_and_unload]
      ▼
src.evaluation.benchmark.BenchmarkRunner  ── same metrics as baseline → results/ + MLflow
```

Integration touch points (no rewrites required, mostly additive):
1. **`requirements.txt`** — add `peft` (and optional `trl`, `bitsandbytes` for CUDA QLoRA).
2. **New `src/training/`** package — dataset builder, LoRA config, train loop, CLI script
   under `scripts/`.
3. **`src/models/model_loader.py`** — extend `load()`/`resolve_model_path()` to detect a
   PEFT adapter dir (`adapter_config.json`) and wrap the base with `PeftModel`. Today the
   checkpoint path assumes a *full* model dir (`config.json` + weights).
4. **`configs/default.yaml`** — add a `training:`/`lora:` block (rank, alpha, dropout,
   target_modules, lr, epochs, batch size, per-task target column).
5. **Reuse** prompt builders and `BenchmarkRunner` unchanged for evaluation.

## 5. Model-Type Branching (causal vs seq2seq)

`is_seq2seq_model()` already distinguishes T5/BART (encoder-decoder) from causal LMs.
LoRA must branch on this:

| Aspect | Causal (codegen, Qwen, starcoder2) | Seq2seq (t5-base/large) |
|--------|-----------------------------------|-------------------------|
| HF class | `AutoModelForCausalLM` | `AutoModelForSeq2SeqLM` |
| PEFT task_type | `CAUSAL_LM` | `SEQ_2_SEQ_LM` |
| LoRA target modules | `q_proj,k_proj,v_proj,o_proj` (Qwen/llama-like), `qkv_proj`/`c_attn` (codegen/starcoder vary) | `q,v` (T5 attention) |
| Labels | prompt+target concatenated, prompt tokens masked (-100) | target only as decoder labels |

This branching is the main correctness-sensitive part of the design.

## 6. Cross-cutting Concerns

- **Reproducibility:** `set_seeds()` (random/numpy/torch, all 42) — call before training.
- **Device:** `resolve_device()` → cuda > mps > cpu. **bitsandbytes 4-bit/QLoRA is
  CUDA-only**; on the macOS/MPS dev host use plain LoRA in fp16/fp32.
- **Caching:** models cached under `models/base/<slug>/` with `.downloaded` marker;
  checkpoints under `models/checkpoints/`.
- **Graceful degradation:** metric libs optional with token-overlap fallback.

This map is synced to `ai-workflow/context/architecture-map.md`.
