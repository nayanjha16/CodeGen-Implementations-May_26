# Text-to-SQL / SQL-to-NoSQL / Text-to-NoSQL — Updated Project Plan (v2)

**Project root:** `C:\WorkArea\codegen\experiment2\`
**Last updated:** 2026-07-30
**Supersedes:** `Updated_plan.md` (2026-07-18)

---

## 1. Project Goal

Fine-tune a small open-source code language model to perform three related database query translation tasks simultaneously, using a Teacher-Student Knowledge Distillation pipeline to progressively improve quality.

| Task | Input | Output |
|------|-------|--------|
| Text-to-SQL | Natural language question + relational schema | SQL query |
| SQL-to-NoSQL | SQL query + MongoDB collection schema | MongoDB MQL query |
| Text-to-NoSQL | Natural language question + MongoDB collection schema | MongoDB MQL query |

---

## 2. Model

| Property | Value |
|----------|-------|
| Base model | `Salesforce/codegen-350M-multi` |
| Architecture | Causal LM (decoder-only) |
| Fine-tuning method | LoRA via PEFT |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| LoRA target modules | `qkv_proj`, `out_proj`, `fc_in`, `fc_out` |
| Trainable parameters | ~5.2M (1.45% of 357M total) |
| Max context window | 2048 tokens |
| Training device | CPU (float32); GPU uses fp16 automatically |

Training hyperparameters (from `src/config.py`):

| Setting | Value |
|---------|-------|
| Epochs | 7 |
| Per-device batch size | 1 (reduced from 4 due to T4 OOM; effective batch unchanged) |
| Gradient accumulation | 16 (effective batch = 16, same as original 4×4) |
| Learning rate | 2e-4 |
| Warmup ratio | 0.03 |
| Weight decay | 0.01 |
| Max output tokens (inference) | 150 |
| Beam search | 4 beams |
| Checkpoint selection | Best epoch by `eval_exact_match` on 5% held-out split |

---

## 3. Datasets

### Spider (Text-to-SQL)
- **Source:** Stanford Spider benchmark
- **Train:** `data/spider/train_spider.json` — 7,000 question/SQL pairs across 166 databases
- **Dev:** `data/spider/dev.json` — 1,034 examples
- **Schema:** `data/spider/tables.json` — DDL for all 166 databases
- **Schema format used in training/inference:** Compact `table(col1, col2->ref.col) | table2(...)` produced by `load_spider_compact_schema_maps_with_fk()`

### DocSpider (SQL-to-NoSQL and Text-to-NoSQL)
- **Source:** Custom MongoDB ground-truth dataset
- **Train:** `docspider/docspider_ground_truth_dataset/train.json` — 4,043 entries
- **Dev:** `docspider/docspider_ground_truth_dataset/dev.json` — 620 examples
- **Collections schema:** `docspider/docspider_ground_truth_dataset/collections.json` — 159 databases
- **Schema format:** Already compact; returned directly by `load_schema_context_map()`

Each DocSpider entry produces **two training samples**:
- Phase A (`sql2nosql`): given the gold SQL, produce the MQL
- Phase B (`text2nosql`): given the NL question, produce the MQL

### Dataset Balancing

DocSpider (4,043 entries × 2 phases = 8,086 samples) is oversampled to match the Spider count (7,000). The unified training set therefore contains:
- 7,000 Spider text2sql samples
- 7,000 DocSpider sql2nosql samples
- 7,000 DocSpider text2nosql samples
- **Total: 21,000 samples per full run**

### Schema Usage — Motivation for Pruning

Analysis of both dev sets shows that full schemas contain substantial noise:

| Metric | Spider (Text-to-SQL) | DocSpider (NoSQL) |
|--------|---------------------|-------------------|
| Avg tables/collections in schema | 4.5 | 4.5 |
| Avg **unused** per query | **3.0 (67% noise)** | **3.0 (67% noise)** |
| Queries using ALL tables | 6% | 9% |
| Queries with 3+ unused tables | 43% | 43% |

This noise wastes token budget and creates false candidate join paths that mislead small models. Schema pruning (§5) addresses this directly.

---

## 4. Training Architecture — Multi-Task Unified Fine-Tuning

A single LoRA adapter is trained on all three tasks simultaneously. Task identity is embedded in the prompt header (`[Task: NL-to-SQL]`, `[Task: SQL-to-MQL]`, `[Task: NL-to-MQL]`), so the model learns to switch behaviour based on the tag.

### Prompt Format (CodeGen)

Each prompt begins with a task tag followed by a natural-language task description block that names each input, enumerates query/clause types, and states output constraints. This structure is consistent across Pass 1, Pass 2, training, and inference.

**Text-to-SQL:**
```
[Task: NL-to-SQL]
You are given a Reference example, a Schema, and a Question. Generate the SQL query that answers the Question.

Input:
- Reference: A similar question with its verified SQL answer. Use it as a structural pattern.
- Schema: Tables and columns available. col->table.col marks foreign key join paths.
- Question: The natural language question to answer.

Question types: counting (COUNT), filtering/WHERE (include ALL conditions — equality, comparison, LIKE, IN, BETWEEN),
aggregation (AVG/SUM/MAX/MIN), ranking (ORDER BY...LIMIT), joining (JOIN via FK paths),
grouping (GROUP BY/HAVING), set operations (UNION/INTERSECT/EXCEPT), subqueries (nested SELECT).

Output: A single SQL query that answers the Question. No explanations or text outside the query.
Rules:
- Use only tables/columns from Schema. Uppercase SQL keywords.
- Include ALL columns, conditions, and clauses needed. Do not simplify or omit.
- Only include ORDER BY, GROUP BY, HAVING when the Question explicitly requires ranking, grouping, or filtered aggregation.
- Query must be syntactically valid, schema-compliant, and complete.

### REFERENCE EXAMPLE ###
Context Question: <example question>
Target SQL: <example SQL>
#########################

### TARGET TASK ###
Question: <question>
Schema: singer(Singer_ID, Name, Age) | concert(Concert_ID, Stadium_ID->stadium.Stadium_ID, Year)
[Broken Draft: <broken SQL>]        ← only present in Pass 2

### SYSTEM RESPONSE ###
```

**Pass 1 Target (bare SQL — no Analysis prefix):**
```
SELECT Name FROM singer ORDER BY Age LIMIT 1
```

**Pass 2 Target (with teacher diagnosis):**
```
Analysis: <one diagnostic sentence> | Corrected_SQL: <gold SQL>
```

**SQL-to-NoSQL:**
```
[Task: SQL-to-MQL]
You are given a Reference example, a Schema, and an Input SQL. Translate the SQL into an equivalent MongoDB MQL query.
...
### SYSTEM RESPONSE ###
```

**Pass 1 Target:** bare MQL. **Pass 2 Target:** `Analysis: <sentence> | Final_MQL: <gold MQL>`

**Text-to-NoSQL:**
```
[Task: NL-to-MQL]
You are given a Reference example, a Schema, and a Question. Generate the MongoDB MQL query that answers the Question.
...
### SYSTEM RESPONSE ###
```

**Pass 1 Target:** bare MQL. **Pass 2 Target:** `Analysis: <sentence> | Final_MQL: <gold MQL>`

**Notes on prompt design:**
- The `### REFERENCE EXAMPLE ###` block is omitted entirely when no example is available (not written as "None").
- The `Broken Draft:` line is omitted when there is no broken draft (not written as "None").
- Pass 1 target is bare SQL/MQL — no Analysis prefix.
- Pass 2 target keeps `Analysis: <teacher diagnosis> | Corrected_SQL/Final_MQL: <gold>`.
- Output extraction in `processor.py` handles both formats.
- Task description enumerates UNION/INTERSECT/EXCEPT and nested subqueries explicitly.
- Schema format includes FK annotations (`col->table.col`) so the model can discover join paths.
- **Schema is now pruned per-query** before insertion into the prompt — see §5.

---

## 5. Schema Pruning RAG

### Background — What Changed from v1

The original RAG approach injected a semantically similar training example (question + gold query pair) as a reference block in every prompt. Evaluation showed this **did not improve accuracy** — the model learned to ignore the reference block for complex queries because random references provided no useful structural pattern.

In v2, the RAG concept is repurposed for **schema pruning**: instead of adding a reference example, RAG is used to select only the schema tables/collections relevant to the current query. Full schemas include an average of 3 unused tables per query (67% noise), which wastes token budget and misleads the model into selecting wrong tables.

The reference-example RAG infrastructure (`Retriever`, existing index files) is retained and still active during training — it continues to inject semantically similar examples. Schema pruning is a separate, additive improvement.

### Schema Noise by the Numbers

From analysis of both dev sets (1,034 Spider + 620 DocSpider examples):
- Only 6–9% of queries require all tables in the schema
- On average, **3 out of 4.5 tables (67%)** in every schema are irrelevant to the query
- For the largest databases (11 tables), a single-table query sees 10 irrelevant tables

### Pruning Strategy per Task

| Task | Method | Rationale |
|------|--------|-----------|
| SQL-to-NoSQL | Parse `FROM`/`JOIN` from input SQL | Input SQL states exact tables — deterministic, no ML |
| Text-to-SQL | BGE cosine similarity + FK expansion | Question doesn't name tables; embedding captures semantic intent |
| Text-to-NoSQL | BGE cosine similarity (no FK expansion) | Same as above; DocSpider has no FK structure |

**SQL-to-NoSQL example:**
```
Input SQL:  SELECT name FROM singer ORDER BY age DESC

Full schema (4 collections, ~180 tokens):
  stadium(...) | concert(...) | singer(...) | singer_in_concert(...)

Pruned schema (1 collection, ~30 tokens):
  singer(Age, Country, Is_male, Name, Singer_ID, ...)

Token reduction: 80%
```

**Text-to-SQL / Text-to-NoSQL — embedding flow:**
1. Question is encoded once with BGE-small (`BAAI/bge-small-en-v1.5`)
2. Each table in the db_id is scored by cosine similarity against pre-built table embeddings
3. Top-3 tables are kept
4. For Spider: FK-connected neighbors of any kept table are added (preserves join paths)
5. Schema string is reconstructed from kept tables in original order

### Train/Inference Consistency

Schema pruning is applied identically during both training and inference — no train/inference mismatch.

| Task | Training | Inference |
|------|----------|-----------|
| SQL-to-NoSQL | Parse FROM/JOIN of gold SQL | Parse FROM/JOIN of input SQL |
| Text-to-SQL | Embed question → top-k tables | Embed question → top-k tables |
| Text-to-NoSQL | Embed question → top-k collections | Embed question → top-k collections |

For SQL-to-NoSQL both sides use oracle information (the SQL always states the exact tables), making it perfectly consistent.

### Pre-built Schema Embedding Index

Table/collection embeddings are pre-computed once and stored in `retrieval_index/`. This avoids re-encoding ~750 table strings on every training run.

| File | Contents | Size |
|------|----------|------|
| `schema_spider_embeddings.npy` | ~747 Spider tables × 384-dim, L2-normalised | ~1.1 MB |
| `schema_spider_metadata.json` | `[{db_id, name, table_str}, ...]` | — |
| `schema_docspider_embeddings.npy` | ~716 DocSpider collections × 384-dim | ~1.0 MB |
| `schema_docspider_metadata.json` | `[{db_id, name, table_str}, ...]` | — |

Built by: `python scripts/build_retrieval_index.py --task schema` (~5 seconds).

The only on-the-fly BGE call at training/inference time is encoding the question itself (one call per sample). Table embeddings are never re-encoded.

### Fallback Behaviour

If the schema index has not been built, or if `db_id` is not in the index, the pruner falls back silently to the full schema. Training and inference both continue unaffected with a logged warning.

---

## 6. Reference-Example RAG (Original)

The original RAG mechanism (injecting a similar training example as a reference block) is still active. It operates independently of schema pruning.

| Phase | Behaviour |
|-------|-----------|
| Training (Pass 1 & Pass 2) | Semantic retrieval (BM25 + dense) fetches the most similar training example per sample |
| Inference (no `--rag` flag) | Reference block omitted |
| Inference (`--rag` flag) | BM25 + dense hybrid retrieval fetches the most semantically similar training example |

**Note:** Reference-example RAG did not improve accuracy in Pass 1 evaluation. The primary evaluation comparison is RAG inference vs RAG inference across passes. Schema pruning (§5) is the new mechanism expected to improve accuracy.

### Reference Retrieval Index

Pre-built embeddings stored in `retrieval_index/`:
```
retrieval_index/
  text2sql_embeddings.npy       (7,000 × 384)
  text2sql_metadata.json
  sql2nosql_embeddings.npy      (4,043 × 384)
  sql2nosql_metadata.json
  text2nosql_embeddings.npy     (4,043 × 384)
  text2nosql_metadata.json
```

Embedding model: `BAAI/bge-small-en-v1.5`.

---

## 7. Teacher-Student Knowledge Distillation

### Overview

```
Pass 1 Fine-tune → Pass 1 Inference → Extract Failures
    → Teacher Annotation → Pass 2 Fine-tune → Pass 2 Inference → Compare
```

### Pass 1 — Standard Multi-Task Training
- Trains from the base CodeGen model with fresh LoRA adapters.
- All three tasks trained simultaneously with schema pruning active.
- Checkpoint saved to `models/codegen_pass1/`.

### Failure Extraction (`extract_failures.py`)
- Loads Pass 1 predictions for all three tasks.
- Normalises SQL (lowercase + whitespace, strip semicolons) and MQL (whitespace).
- Writes failure records (with `broken_draft` field) to:
  - `data/spider/text2sql_failures.json`
  - `docspider/docspider_ground_truth_dataset/sql2nosql_failures.json`
  - `docspider/docspider_ground_truth_dataset/text2nosql_failures.json`

### Teacher Annotation (`generate_teacher_data.py`)
- Calls a configurable LLM (default: Groq) for each failure.
- Teacher receives: the failure's input, the broken draft, the gold label, and a RAG reference example.
- Teacher outputs (JSON):
  - `teacher_analysis`: one diagnostic sentence (max 35 words)
  - `corrected_query`: verified against gold; gold is always used for training
- Failure records annotated with `teacher_analysis` and merged back into the full training set.
- DocSpider uses separate field names per task variant:
  - `broken_draft_trans` / `teacher_analysis_trans` (sql2nosql)
  - `broken_draft_dir` / `teacher_analysis_dir` (text2nosql)

### Teacher Config (`src/config.py → TEACHER`)

```python
TEACHER = {
    "provider":           "groq",
    "base_url":           "https://api.groq.com/openai/v1",
    "model_id":           "llama-3.3-70b-versatile",
    "temperature":        0.2,
    "max_output_tokens":  450,
    "analysis_max_words": 35,
    "rate_limit_sleep":   0.1,
    "max_failures":       3000,
}
```

Override at runtime: `python generate_teacher_data.py --provider together --model_id defog/sqlcoder-70b-alpha`

### Pass 2 — Teacher-Calibrated Fine-Tuning
- Continues training **from Pass 1 weights** (not from scratch).
- Uses augmented datasets that include teacher analyses in prompts.
- Schema pruning remains active in Pass 2.
- Checkpoint saved to `models/codegen_pass2/`.

---

## 8. Full Pipeline — File Reference

### Entry Points

| Script | Purpose | Key Arguments |
|--------|---------|---------------|
| `run_codegen.py` | Orchestrator — runs all 7 stages in sequence | `--start_from`, `--skip_rag`, `--sanity` |
| `finetune_unified.py` | Multi-task fine-tuning (Pass 1 and Pass 2) | `--spider_data`, `--docspider_data`, `--checkpoint_dir`, `--resume_from`, `--limit`, `--no_rag` |
| `run_multi_task_inference.py` | Inference for one task | `--task`, `--rag`, `--checkpoint_override`, `--output_dir`, `--limit` |
| `extract_failures.py` | Extract Pass 1 failures for teacher annotation | `--text2sql_pred`, `--sql2nosql_pred`, `--text2nosql_pred` |
| `generate_teacher_data.py` | Call teacher LLM and merge annotations | `--provider`, `--model_id`, `--mock_teacher` |
| `scripts/build_retrieval_index.py` | Build retrieval and schema pruning indices | `--task [text2sql\|sql2nosql\|text2nosql\|schema]` |
| `compare_results.py` | Side-by-side Pass 1 vs Pass 2 evaluation report | — |

### Source Library (`src/`)

| Module | Responsibility |
|--------|---------------|
| `src/config.py` | All hyperparameters, paths, teacher config |
| `src/logger.py` | `UnifiedLogger` — timestamped plain-text log files, one per subprocess |
| `src/loader.py` | Dataset loaders, schema loaders, `load_spider_fk_neighbors_map()` |
| `src/prompt_builder.py` | Prompt construction for all 3 tasks; accepts `schema_pruner=` param |
| `src/schema_pruner.py` | **New (v2)** — `SchemaPruner` class; per-query schema trimming for all 3 tasks |
| `src/model_factory.py` | Load base model, inject LoRA, load saved checkpoint |
| `src/generator.py` | `generate_sql_prediction()` and `generate_nosql_prediction()` |
| `src/processor.py` | `clean_generated_sql()` and `clean_generated_nosql()` |
| `src/retriever.py` | BM25 + dense hybrid retriever for reference-example RAG |

### Data & Output Layout

```
experiment2/
├── data/spider/
│   ├── train_spider.json           # 7,000 training examples
│   ├── dev.json                    # 1,034 dev examples
│   ├── tables.json                 # Schema DDL for 166 databases
│   ├── text2sql_failures.json      # Written by extract_failures.py
│   └── spider_augmented_train.json # Written by generate_teacher_data.py
│
├── docspider/docspider_ground_truth_dataset/
│   ├── train.json                  # 4,043 training entries
│   ├── dev.json                    # 620 dev examples
│   ├── collections.json            # Collection schemas for 159 databases
│   ├── sql2nosql_failures.json     # Written by extract_failures.py
│   ├── text2nosql_failures.json    # Written by extract_failures.py
│   └── train_augmented.json        # Written by generate_teacher_data.py
│
├── models/
│   ├── codegen_pass1/              # Pass 1 LoRA checkpoint
│   └── codegen_pass2/              # Pass 2 LoRA checkpoint
│
├── outputs/
│   └── codegen/
│       ├── pass1/
│       │   ├── text2sql/predictions.json
│       │   ├── sql2nosql/predictions.json
│       │   └── text2nosql/predictions.json
│       └── pass2/
│           ├── text2sql/predictions.json        (no-RAG)
│           ├── text2sql/predictions_rag.json    (with RAG)
│           ├── sql2nosql/predictions.json
│           ├── sql2nosql/predictions_rag.json
│           ├── text2nosql/predictions.json
│           └── text2nosql/predictions_rag.json
│
├── retrieval_index/
│   ├── text2sql_embeddings.npy         # Reference-example RAG index (7k examples)
│   ├── text2sql_metadata.json
│   ├── sql2nosql_embeddings.npy
│   ├── sql2nosql_metadata.json
│   ├── text2nosql_embeddings.npy
│   ├── text2nosql_metadata.json
│   ├── schema_spider_embeddings.npy    # NEW (v2) — schema pruning index (~747 tables)
│   ├── schema_spider_metadata.json
│   ├── schema_docspider_embeddings.npy # NEW (v2) — schema pruning index (~716 collections)
│   └── schema_docspider_metadata.json
│
└── logs/
    └── <script>_<YYYYMMDD>_<HHMMSS>.log   # One file per subprocess, UTF-8
```

---

## 9. How to Run

### One-time setup: build the schema pruning index (NEW in v2)

**Must be run once before the first training run**, and again if `data/spider/tables.json` or `docspider/.../collections.json` change.

```bash
python scripts/build_retrieval_index.py --task schema
```

This writes the four `schema_*` files into `retrieval_index/` in under 5 seconds.

To build all indices at once (reference-example RAG + schema pruning):
```bash
python scripts/build_retrieval_index.py
```

### Full pipeline (all 7 stages)
```bash
python run_codegen.py
```

### Resume from a specific stage
```bash
python run_codegen.py --start_from inference     # skip Pass 1 training
python run_codegen.py --start_from teacher       # skip to teacher annotation
python run_codegen.py --start_from pass2         # skip to Pass 2 fine-tune
python run_codegen.py --start_from pass2_infer   # skip to Pass 2 inference
python run_codegen.py --start_from compare       # skip to final comparison
```

### Skip reference-example RAG (faster, CPU-friendly)
```bash
python run_codegen.py --skip_rag
```

Note: `--skip_rag` disables the **reference-example** RAG only. Schema pruning is always active regardless of this flag.

### Sanity test (3 samples, teacher mocked)
```bash
python run_codegen.py --sanity
```

### Teacher with Anthropic instead of Groq
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python generate_teacher_data.py --provider anthropic --model_id claude-haiku-4-5-20251001
```

---

## 10. Pipeline Stage Sequence

| # | Stage key | Script | Reads | Writes |
|---|-----------|--------|-------|--------|
| 1 | `train` | `finetune_unified.py` | `spider/train_spider.json`, `docspider/train.json`, schema index | `models/codegen_pass1/` |
| 2 | `inference` | `run_multi_task_inference.py` ×3 | `spider/dev.json`, `docspider/dev.json`, `models/codegen_pass1/`, schema index | `outputs/codegen/pass1/*/predictions.json` |
| 3 | `extract` | `extract_failures.py` | Pass 1 predictions | `*_failures.json` |
| 4 | `teacher` | `generate_teacher_data.py` | failures, training sets, teacher API | `spider_augmented_train.json`, `train_augmented.json` |
| 5 | `pass2` | `finetune_unified.py` | augmented training sets, `models/codegen_pass1/`, schema index | `models/codegen_pass2/` |
| 6 | `pass2_infer` | `run_multi_task_inference.py` ×3 (+RAG variants) | `spider/dev.json`, `docspider/dev.json`, `models/codegen_pass2/`, schema index | `outputs/codegen/pass2/*/predictions*.json` |
| 7 | `compare` | `compare_results.py` | Pass 1 and Pass 2 predictions | `outputs/comparison_report.txt` |

---

## 11. Logging

Each subprocess creates its own log file named `<script>_<YYYYMMDD>_<HHMMSS>.log` in the `logs/` directory.

Log level: file receives INFO and above; terminal receives WARNING and above only.

Log entry format:
```
2026-07-30 14:16:52,697 [INFO   ] [fine_tuning] spider_sample_preview  index=0  db_id=...  prompt_tokens=148
  >> INPUT  : [Task: NL-to-SQL] ...
  >> OUTPUT : SELECT count(*) FROM head ...
```

Schema pruner events logged as:
- `schema_pruner_loaded` — index loaded successfully at startup
- `schema_pruner_unavailable` — index missing; full schema used (warning)

---

## 12. Evaluation

### Text-to-SQL
Uses the official Spider evaluation harness (`evaluation.py`) with match-based scoring.

**Known issue:** Requires `process_sql.py` to be on the Python path. Predictions are saved regardless.

### SQL-to-NoSQL and Text-to-NoSQL
Uses `stage5_evaluate_by_execution.py` (DocSpider execution harness) which runs predictions against a live MongoDB instance and scores by result-set equality.

Results categorised by difficulty (EASY / MEDIUM / HARD / EXTRA) and saved as `evaluation_report.txt` / `evaluation_report_rag.txt`.

---

## 13. Schema Handling

### Spider (Text-to-SQL)
Both training and inference call `load_spider_compact_schema_maps_with_fk()` (in `src/loader.py`), which builds compact schemas from `tables.json` with FK annotations:

```
singer(Singer_ID, Name, Age) | concert(Concert_ID, Stadium_ID->stadium.Stadium_ID, Year) | singer_in_concert(concert_id->concert.Concert_ID, singer_id->singer.Singer_ID)
```

Schema pruning is applied **after** this full schema is loaded, trimming it to relevant tables only before the prompt is built.

`load_spider_fk_neighbors_map()` (new in v2) returns `{db_id: {table: [fk_connected_tables]}}` and is used by `SchemaPruner` to expand the kept table set with join-path neighbors.

### DocSpider (SQL-to-NoSQL, Text-to-NoSQL)
`load_schema_context_map()` returns compact format from `collections.json`. Schema pruning is applied after this step. DocSpider has no FK structure, so FK expansion is not performed.

---

## 14. Known Issues & Fixes Applied

| Issue | Status | Fix |
|-------|--------|-----|
| Log files all named `pipeline_TIMESTAMP.log` — no stage label | Fixed | Logger derives prefix from `sys.argv[0]` automatically |
| `—` em-dash appeared as `?` in log files (Windows encoding) | Fixed | `FileHandler` now uses `encoding='utf-8'` |
| `### REFERENCE EXAMPLE ###\nNone` in inference prompts | Fixed | Reference block omitted entirely when no example available |
| `steps_per_epoch=0` in training log with small datasets | Fixed | Changed to ceiling division with `max(1, ...)` |
| Text2SQL inference used verbose CREATE TABLE schema; model trained on compact format | Fixed | `minify_sql_schema()` moved to `src/loader.py` and applied in inference |
| Pass 2 RAG inference ignored `--limit` flag | Fixed | `*extra` args now passed to RAG inference call in `stage_pass2_inference()` |
| `Broken Draft: None` appearing in prompts when no broken draft exists | Fixed | Conditional `draft_line` in all three prompt builders |
| Pass 1/2 inference used greedy decoding despite `num_beams=2` in config | Fixed | `NUM_BEAMS` now read from config; value raised to 4 |
| Best checkpoint selected by `eval_loss` (poor proxy for SQL accuracy) | Fixed | `compute_metrics` + `preprocess_logits_for_metrics` added; checkpoint selected by `eval_exact_match` |
| Pass 2 fine-tuning epoch checkpoints lost on Colab disconnect | Fixed | `--checkpoint_dir` + `--resume_training` flags added to `finetune_unified.py` |
| Teacher fallback analysis was generic for all task types | Fixed | Separate fallback strings per task in `_FALLBACK_ANALYSES` dict |
| Teacher `analysis_max_words=15` produced truncated unhelpful analyses | Fixed | Raised to 35 words; `max_output_tokens` raised to 450 |
| Full schema (67% noise on average) fed to model for every query | Fixed (v2) | `SchemaPruner` trims schema to relevant tables only — see §5 |

---

## 15. Outstanding Notes

- **Build schema index before training:** Run `python scripts/build_retrieval_index.py --task schema` once before the first training run on Colab. Without this, the pruner falls back gracefully to full schemas but the improvement is lost.

- **`process_sql` missing for Spider evaluation:** Predictions are saved regardless; evaluate manually or fix the Python path.

- **Pass 2 `has_teacher_data=False` in sanity run:** Expected. Sanity inference runs on the dev set; teacher merge keys on training-set `(db_id, question)` pairs — no overlap. Correct in full runs.

- **CPU-only environment:** Full pipeline (21,000 samples, 7 epochs) is intended for GPU. Use `--sanity` or `--skip_rag` on CPU.

- **Teacher API key:** Default provider is Groq (free). Set `GROQ_API_KEY` before Stage 4. Use `--mock_teacher` to bypass without a key.

- **Batch size 1 on T4:** T4 OOMed with `train_batch=4` on 2048-token sequences. `train_batch=1, grad_accum=16` gives identical effective batch of 16 at ~20–30% slower wall-clock per epoch.

- **Schema pruning top_k=3:** The default keeps the 3 most relevant tables plus FK neighbors. For databases with complex 4+ table joins, this may occasionally miss a table. If Pass 1 accuracy on multi-join queries is still low, consider raising `_TOP_K_DEFAULT` in `src/schema_pruner.py` to 4.

- **Reference-example RAG did not improve Pass 1 accuracy:** The `--skip_rag` flag disables reference-example injection at training time. Schema pruning is the new primary accuracy lever in v2. The `--rag` inference flag is still available for comparison but is not expected to be the main signal.

- **Pass 1 eval_loss pattern (from v1):** Pass 1 training showed monotonically decreasing eval_loss across all 5 epochs, suggesting the model had not fully converged. Epochs raised to 7 in v2.
