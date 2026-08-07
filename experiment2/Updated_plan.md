# Text-to-SQL / SQL-to-NoSQL / Text-to-NoSQL — Updated Project Plan

**Project root:** `C:\WorkArea\codegen\experiment2\`
**Last updated:** 2026-07-18

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
| Epochs | 5 |
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
- **Schema format used in training/inference:** Compact `table(col1, col2) | table2(...)` produced by `minify_sql_schema()`

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

Input:
- Reference: A similar SQL with its verified MQL translation. Use it as a mapping pattern.
- Schema: Collections and fields available. field->collection.field marks references.
- Input SQL: The relational SQL query to translate.

Clause mapping: WHERE->$match, GROUP BY->$group, ORDER BY->$sort, LIMIT->$limit, SELECT fields->$project, JOIN->$lookup.

Output: A single MQL query (db.collection.find or aggregate pipeline). No explanations or text outside the query.
Rules:
- Use only collections/fields from Schema.
- Include ALL clauses from Input SQL. Do not simplify or omit.
- Query must be syntactically valid, schema-compliant, and semantically equivalent to Input SQL.

### REFERENCE EXAMPLE ###
Input SQL: <example SQL>
Target MQL: <example MQL>
#########################

### TARGET TASK ###
Input SQL: <input SQL>
Schema: concert(Concert_ID, Stadium_ID->stadium.Stadium_ID, Year) | stadium(Stadium_ID, Name)
[Broken Draft: <broken MQL>]

### SYSTEM RESPONSE ###
```

**Pass 1 Target:** bare MQL. **Pass 2 Target:** `Analysis: <sentence> | Final_MQL: <gold MQL>`

**Text-to-NoSQL:**
```
[Task: NL-to-MQL]
You are given a Reference example, a Schema, and a Question. Generate the MongoDB MQL query that answers the Question.

Input:
- Reference: A similar question with its verified MQL answer. Use it as a structural pattern.
- Schema: Collections and fields available. field->collection.field marks references.
- Question: The natural language question to answer.

Query types: counting (countDocuments/$count), filtering ($match — include ALL conditions),
aggregation ($group), sorting ($sort), limiting ($limit), projecting fields ($project),
set operations ($unionWith), subqueries (nested pipeline stages).

Output: A single MQL query that answers the Question. No explanations or text outside the query.
Rules:
- Use only collections/fields from Schema.
- Include ALL conditions and operators needed. Do not simplify or omit.
- Only include $sort, $group, $limit when the Question explicitly requires ranking, grouping, or limiting.
- Query must be syntactically valid, schema-compliant, and complete.

### REFERENCE EXAMPLE ###
Context Question: <example question>
Target MQL: <example MQL>
#########################

### TARGET TASK ###
Question: <question>
Schema: concert(Concert_ID, Stadium_ID->stadium.Stadium_ID, Year) | stadium(Stadium_ID, Name)
[Broken Draft: <broken MQL>]

### SYSTEM RESPONSE ###
```

**Pass 1 Target:** bare MQL. **Pass 2 Target:** `Analysis: <sentence> | Final_MQL: <gold MQL>`

**Notes on prompt design:**
- The `### REFERENCE EXAMPLE ###` block is omitted entirely when no example is available (not written as "None").
- The `Broken Draft:` line is omitted when there is no broken draft (not written as "None").
- Pass 1 target is bare SQL/MQL — no Analysis prefix. The analysis-prefix format adds no signal when the analysis text is a placeholder, and forces the model to learn a useless output pattern. Removing it addresses the precision>recall pattern observed in Pass 1 results (model was generating simpler/shorter outputs).
- Pass 2 target keeps `Analysis: <teacher diagnosis> | Corrected_SQL/Final_MQL: <gold>` — the teacher diagnosis is real and the chain-of-thought helps the model correct errors.
- Output extraction in `processor.py` handles both formats: splits on `Corrected_SQL:`/`Final_MQL:` if present, otherwise processes raw lines directly.
- Task description enumerates UNION/INTERSECT/EXCEPT and nested subqueries explicitly — Pass 1 IUEN recall was ~0, indicating the model never attempted set operations without a direct prompt signal.
- Schema format includes FK annotations (`col->table.col`) so the model can discover join paths without needing full DDL.

---

## 5. RAG — Retrieval-Augmented Generation

RAG provides a reference example (similar question/query pair) in the prompt to help the model generalise.

| Phase | Behaviour |
|-------|-----------|
| Training (Pass 1 & Pass 2) | Semantic retrieval (BM25 + dense) fetches the most similar training example per sample; falls back to random if the index is not yet built |
| Inference (no `--rag` flag) | Reference block is **omitted entirely** (residual train-inference mismatch) |
| Inference (`--rag` flag) | BM25 + dense hybrid retrieval fetches the most semantically similar training example |

**Why training now uses semantic retrieval:**
- A random reference for a complex query (e.g. one requiring UNION or a nested subquery) provides no useful structural pattern — the model learns to ignore the reference block.
- Pass 1 results showed IUEN recall of ~0 and consistent precision > recall across all clause types, indicating the model was producing simpler outputs than needed. A semantically matched reference gives the model a template that matches the query's complexity.
- The retrieval index is built from the training set by `scripts/build_retrieval_index.py` and is pre-loaded once per training run (not per epoch). The cost is a one-time ~30-second retrieval sweep over 21,000 samples at dataset-construction time, not repeated each epoch.
- Self-match is avoided by retrieving k=2 and skipping the result whose question/SQL matches the current sample.

**Residual train-inference mismatch (no-RAG inference):**
No-RAG inference still omits the reference block, which differs from how the model was trained. The primary evaluation comparison is **RAG inference vs RAG inference** (Pass 1 RAG vs Pass 2 RAG). No-RAG inference scores will be lower and are not the meaningful signal.

### Retrieval Index

Pre-built embeddings stored in `retrieval_index/`:
```
retrieval_index/
  text2sql_embeddings.npy
  text2sql_metadata.json
  sql2nosql_embeddings.npy
  sql2nosql_metadata.json
  text2nosql_embeddings.npy
  text2nosql_metadata.json
```

Built by `scripts/build_retrieval_index.py`. The pipeline auto-builds the index if any file is missing (checked in `stage_ensure_retrieval_index()` inside `run_codegen.py`).

Embedding model: `BAAI/bge-small-en-v1.5` (via `sentence-transformers`).

---

## 6. Teacher-Student Knowledge Distillation

### Overview

The pipeline runs in two passes:

```
Pass 1 Fine-tune → Pass 1 Inference → Extract Failures
    → Teacher Annotation → Pass 2 Fine-tune → Pass 2 Inference → Compare
```

### Pass 1 — Standard Multi-Task Training
- Trains from the base CodeGen model with fresh LoRA adapters.
- All three tasks trained simultaneously.
- Random in-domain example injected as reference (RAG for training).
- Checkpoint saved to `models/codegen_pass1/`.

### Failure Extraction (`extract_failures.py`)
- Loads Pass 1 predictions for all three tasks.
- Normalises SQL (lowercase + whitespace, strip semicolons) and MQL (whitespace) before comparison.
- Writes failure records (with `broken_draft` field) to:
  - `data/spider/text2sql_failures.json`
  - `docspider/docspider_ground_truth_dataset/sql2nosql_failures.json`
  - `docspider/docspider_ground_truth_dataset/text2nosql_failures.json`

### Teacher Annotation (`generate_teacher_data.py`)
- Calls a configurable LLM (OpenAI or Anthropic) for each failure.
- Teacher receives: the failure's input, the broken draft, the gold label, and a RAG reference example from the same or a similar database.
- Teacher outputs (JSON):
  - `teacher_analysis`: one diagnostic sentence (max 15 words)
  - `corrected_query`: verified against gold; gold is always used for training
- Failure records annotated with `teacher_analysis` and merged back into the full training set:
  - Spider → `data/spider/spider_augmented_train.json`
  - DocSpider → `docspider/docspider_ground_truth_dataset/train_augmented.json`
- DocSpider uses separate field names per task variant to allow one entry to carry corrections for both task types:
  - `broken_draft_trans` / `teacher_analysis_trans` (sql2nosql)
  - `broken_draft_dir` / `teacher_analysis_dir` (text2nosql)

### Teacher Config (`src/config.py → TEACHER`)

```python
TEACHER = {
    "provider":           "groq",         # default: free, no credit card needed
    "base_url":           "https://api.groq.com/openai/v1",
    "model_id":           "llama-3.3-70b-versatile",
    # Alternatives:
    #   Together (best SQL)  provider="together", model_id="defog/sqlcoder-70b-alpha"
    #   OpenAI               provider="openai",   model_id="gpt-4o-mini", base_url=None
    #   Anthropic            provider="anthropic", model_id="claude-haiku-4-5-20251001"
    "temperature":        0.2,
    "max_output_tokens":  450,
    "analysis_max_words": 35,
    "rate_limit_sleep":   0.1,
    "max_failures":       3000,
}
```

All providers except Anthropic use the OpenAI-compatible client (`openai.OpenAI(base_url=...)`) so switching provider requires only a config change. Set the matching env var: `GROQ_API_KEY`, `TOGETHER_API_KEY`, `FIREWORKS_API_KEY`, or `OPENAI_API_KEY`.

Override at runtime: `python generate_teacher_data.py --provider together --model_id defog/sqlcoder-70b-alpha`

### Pass 2 — Teacher-Calibrated Fine-Tuning
- Continues training **from Pass 1 weights** (not from scratch).
- Uses augmented datasets that include teacher analyses in prompts.
- Detection of Pass 2 mode: `has_teacher_data = any("broken_draft" in t and t["broken_draft"] not in ("", "SELECT * FROM fallback;") for t in spider_tasks)`
- Checkpoint saved to `models/codegen_pass2/`.
- Pass 1 checkpoint is preserved for side-by-side comparison.

---

## 7. Full Pipeline — File Reference

### Entry Points

| Script | Purpose | Key Arguments |
|--------|---------|---------------|
| `run_codegen.py` | Orchestrator — runs all 7 stages in sequence | `--start_from`, `--skip_rag`, `--sanity` |
| `finetune_unified.py` | Multi-task fine-tuning (Pass 1 and Pass 2) | `--spider_data`, `--docspider_data`, `--checkpoint_dir`, `--resume_from`, `--limit` |
| `run_multi_task_inference.py` | Inference for one task | `--task`, `--rag`, `--checkpoint_override`, `--output_dir`, `--limit` |
| `extract_failures.py` | Extract Pass 1 failures for teacher annotation | `--text2sql_pred`, `--sql2nosql_pred`, `--text2nosql_pred` |
| `generate_teacher_data.py` | Call teacher LLM and merge annotations | `--provider`, `--model_id`, `--mock_teacher` |
| `scripts/build_retrieval_index.py` | Build BM25 + dense retrieval index | — |
| `compare_results.py` | Side-by-side Pass 1 vs Pass 2 evaluation report | — |

### Source Library (`src/`)

| Module | Responsibility |
|--------|---------------|
| `src/config.py` | All hyperparameters, paths, teacher config |
| `src/logger.py` | `UnifiedLogger` — timestamped plain-text log files, one per subprocess |
| `src/loader.py` | Dataset loaders, schema loaders, `minify_sql_schema()` |
| `src/prompt_builder.py` | Prompt construction for all 3 tasks (training and inference) |
| `src/model_factory.py` | Load base model, inject LoRA, load saved checkpoint |
| `src/generator.py` | `generate_sql_prediction()` and `generate_nosql_prediction()` |
| `src/processor.py` | `clean_generated_sql()` and `clean_generated_nosql()` — extract SQL/MQL from model output |
| `src/retriever.py` | BM25 + dense hybrid retriever, per-task `retrieve_text2sql/sql2nosql/text2nosql()` |

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
│   ├── text2sql_embeddings.npy
│   ├── text2sql_metadata.json
│   ├── sql2nosql_embeddings.npy
│   ├── sql2nosql_metadata.json
│   ├── text2nosql_embeddings.npy
│   └── text2nosql_metadata.json
│
└── logs/
    └── <script>_<YYYYMMDD>_<HHMMSS>.log   # One file per subprocess, UTF-8
```

---

## 8. How to Run

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

### Skip RAG inference (faster, CPU-friendly)
```bash
python run_codegen.py --skip_rag
```

### Sanity test (3 samples, teacher mocked)
```bash
python run_codegen.py --sanity
```
This caps every stage at 3 samples and bypasses the teacher API call entirely, producing synthetic annotations. Useful to verify the full pipeline runs end-to-end before committing to a full training run.

### Teacher with Anthropic instead of OpenAI
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python generate_teacher_data.py --provider anthropic --model_id claude-haiku-4-5-20251001
```

---

## 9. Pipeline Stage Sequence

| # | Stage key | Script | Reads | Writes |
|---|-----------|--------|-------|--------|
| 1 | `train` | `finetune_unified.py` | `spider/train_spider.json`, `docspider/train.json` | `models/codegen_pass1/` |
| 2 | `inference` | `run_multi_task_inference.py` ×3 | `spider/dev.json`, `docspider/dev.json`, `models/codegen_pass1/` | `outputs/codegen/pass1/*/predictions.json` |
| 3 | `extract` | `extract_failures.py` | Pass 1 predictions | `*_failures.json` |
| 4 | `teacher` | `generate_teacher_data.py` | failures, training sets, teacher API | `spider_augmented_train.json`, `train_augmented.json` |
| 5 | `pass2` | `finetune_unified.py` | augmented training sets, `models/codegen_pass1/` | `models/codegen_pass2/` |
| 6 | `pass2_infer` | `run_multi_task_inference.py` ×3 (+RAG variants) | `spider/dev.json`, `docspider/dev.json`, `models/codegen_pass2/` | `outputs/codegen/pass2/*/predictions*.json` |
| 7 | `compare` | `compare_results.py` | Pass 1 and Pass 2 predictions | `outputs/comparison_report.txt` |

---

## 10. Logging

Each subprocess creates its own log file named `<script>_<YYYYMMDD>_<HHMMSS>.log` in the `logs/` directory. Example after a full run:

```
logs/
  run_codegen_20260711_141606.log          ← orchestrator events
  finetune_unified_20260711_141648.log     ← Pass 1 training, sample previews
  run_multi_task_inference_20260711_141922.log  ← Pass 1 text2sql inference
  run_multi_task_inference_20260711_142040.log  ← Pass 1 sql2nosql inference
  run_multi_task_inference_20260711_142156.log  ← Pass 1 text2nosql inference
  extract_failures_20260711_142248.log     ← failure counts per task
  generate_teacher_data_20260711_142251.log ← teacher prompts (every 50th)
  finetune_unified_20260711_142320.log     ← Pass 2 training
  run_multi_task_inference_20260711_142550.log  ← Pass 2 text2sql inference
  ...
```

Log level: file receives INFO and above; terminal receives WARNING and above only (keeps terminal output clean during long training runs). All files are UTF-8 encoded.

Each log entry format:
```
2026-07-11 14:16:52,697 [INFO   ] [fine_tuning] spider_sample_preview  index=0  db_id=...  prompt_tokens=148
  >> INPUT  : [Task: NL-to-SQL] ...
  >> OUTPUT : Analysis: ... | Corrected_SQL: SELECT count(*) FROM head ...
```

---

## 11. Evaluation

### Text-to-SQL
Uses the official Spider evaluation harness (`evaluation.py`) with match-based scoring.

**Known issue:** Requires `process_sql.py` to be on the Python path. If this module is missing, the evaluation subprocess will fail with `ModuleNotFoundError: No module named 'process_sql'`, but the predictions JSON is still saved and can be evaluated separately.

### SQL-to-NoSQL and Text-to-NoSQL
Uses `stage5_evaluate_by_execution.py` (DocSpider execution harness) which runs predictions against a live MongoDB instance and scores by result-set equality.

Results are categorised by difficulty (EASY / MEDIUM / HARD / EXTRA) and saved alongside predictions as `evaluation_report.txt` and `evaluation_report_rag.txt`.

---

## 12. Schema Handling

### Spider (Text-to-SQL)
Both training and inference now call `load_spider_compact_schema_maps_with_fk()` (in `src/loader.py`), which builds compact schemas directly from `tables.json` and includes FK annotations:

```
# Old compact format (no FK — join paths invisible to model):
singer(Singer_ID, Name, Age) | concert(Concert_ID, Stadium_ID, Year) | singer_in_concert(concert_id, singer_id)

# New compact format with FK annotations:
singer(Singer_ID, Name, Age) | concert(Concert_ID, Stadium_ID->stadium.Stadium_ID, Year) | singer_in_concert(concert_id->concert.Concert_ID, singer_id->singer.Singer_ID)
```

The `->table.col` suffix on a column tells the model which table to JOIN and on which column, without the token cost of full `CREATE TABLE` DDL. This directly addresses the low WHERE and JOIN recall in Pass 1 results.

The old `load_spider_schema_maps()` + `minify_sql_schema()` pipeline is retained in `src/loader.py` for backwards compatibility but is no longer called by the main training or inference scripts.

### DocSpider (SQL-to-NoSQL, Text-to-NoSQL)
Unchanged — `load_schema_context_map()` returns compact format from `collections.json` directly. DocSpider does not have a FK structure equivalent to Spider's `foreign_keys` array.

---

## 13. Known Issues & Fixes Applied

| Issue | Status | Fix |
|-------|--------|-----|
| Log files all named `pipeline_TIMESTAMP.log` — no stage label | Fixed | Logger derives prefix from `sys.argv[0]` automatically |
| `—` em-dash appeared as `?` in log files (Windows encoding) | Fixed | `FileHandler` now uses `encoding='utf-8'` |
| `### REFERENCE EXAMPLE ###\nNone` in inference prompts | Fixed | Reference block omitted entirely when no example is available |
| `steps_per_epoch=0` in training log with small datasets | Fixed | Changed to ceiling division with `max(1, ...)` |
| Text2SQL inference used verbose CREATE TABLE schema; model trained on compact format | Fixed | `minify_sql_schema()` moved to `src/loader.py` and applied in inference |
| Pass 2 RAG inference ignored `--limit` flag (ran all 1,034 samples in sanity mode) | Fixed | `*extra` args now passed to RAG inference call in `stage_pass2_inference()` |
| `Broken Draft: None` appearing in prompts when no broken draft exists | Fixed | Conditional `draft_line` in all three prompt builders |
| `[cite: 1]` artifact in training print statements | Fixed | Removed |
| Pass 1/2 inference used greedy decoding despite `num_beams=2` in config | Fixed | `NUM_BEAMS` now read from config and passed to `model.generate()` in `src/generator.py`; value raised to 4 |
| Best checkpoint selected by `eval_loss` (poor proxy for SQL accuracy) | Fixed | Added `compute_metrics` + `preprocess_logits_for_metrics` to `finetune_unified.py`; checkpoint now selected by `eval_exact_match` |
| Pass 2 fine-tuning epoch checkpoints lost on Colab disconnect | Fixed | Colab notebook now passes `--checkpoint_dir` pointing to Google Drive; `--resume_training` flag added to `finetune_unified.py` for reconnect resumption |
| Teacher fallback analysis was generic for all task types | Fixed | Separate fallback strings per task in `_FALLBACK_ANALYSES` dict in `generate_teacher_data.py` |
| Teacher `analysis_max_words=15` produced truncated unhelpful analyses | Fixed | Raised to 35 words; `max_output_tokens` raised from 300 to 450 |

---

## 14. Outstanding Notes

- **`process_sql` missing for Spider evaluation**: The Spider eval harness depends on `process_sql.py` being importable. Predictions are saved regardless; evaluate manually or fix the Python path if needed.
- **Pass 2 `has_teacher_data=False` in sanity run**: Expected. Sanity inference runs on the dev set, but the teacher merge keys on training-set `(db_id, question)` pairs — no overlap. In a full run, failures come from the training data and the merge will find matches correctly.
- **CPU-only environment**: All runs on CPU take significantly longer. The full pipeline (21,000 training samples, 5 epochs) is intended for GPU execution. On CPU, use `--sanity` or `--skip_rag` to reduce runtime.
- **Teacher API key**: Default provider is Groq (free). Get a key at `console.groq.com`. Set `GROQ_API_KEY` before running Stage 4. Without any key, use `--mock_teacher` to bypass the API call.
- **Batch size reduced to 1 on T4**: T4 (16 GB) OOMed with `train_batch=4` due to 2048-token sequences. Changed to `train_batch=1, grad_accum=16` — effective batch is unchanged at 16. Training is ~20–30% slower per epoch but mathematically equivalent.
- **Pass 1 eval_loss pattern**: Pass 1 training showed monotonically decreasing eval_loss across all 5 epochs (0.0774 → 0.0298), with no plateau at epoch 5. This suggests the model had not fully converged. If Stage 2 accuracy is below expectations, increasing epochs to 8–10 in `src/config.py` and re-running Pass 1 is the first thing to try.
- **Pass 1 text2sql exact match 23.2% with precision > recall across all clause types**: Addressed in the prompt/schema redesign — see §4 and §12. Key fixes: bare SQL output for Pass 1, task description with full query-type taxonomy, FK schema annotations, semantic RAG in training.
