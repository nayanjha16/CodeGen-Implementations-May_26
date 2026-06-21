# Risk Analysis — PEFT / LoRA Initiative

Severity legend: **High** (blocking/correctness), **Medium** (reliability/quality),
**Low** (polish/maintainability).

## 1. Data Risks

### [High] Training data is essentially empty
`data/TEND/` holds only **10 train + 10 validation rows** (smoke-test output). LoRA on 10
examples will overfit instantly and learn nothing generalizable.
- **Mitigation**: regenerate the **full Spider train split (~7k)** and a real validation
  split via `python scripts/run_all_tend.py`. Budget time — Qwen documentation generation
  is slow on CPU/MPS. Consider `--no-doc`/`--no-eval` for the SQL tasks and a separate doc
  pass, or generate docs only for the subset used for nosql2doc.

### [Medium] Documentation targets are model-generated, not gold
The `documentation` column is produced by **Qwen2.5-0.5B-Instruct**, not human-authored.
Training a model to imitate a 0.5B model's output caps quality at the teacher and can
amplify its errors/hallucinations. The Qwen semantic judge is the *same* family — circular.
- **Mitigation**: treat doc supervision as **distillation**; sample-audit targets; consider
  a stronger teacher or the rule-based `ReferenceDocumentationBuilder` as an alternative
  reference. Report metrics against both teacher and rule-based reference.

### [Medium] sql2nosql / nosql2doc targets inherit rule-based converter limits
`nosql_query` comes from `SQLToNoSQLTranslator` (sql-mongo-converter), which warns/omits
JOIN, HAVING, UNION, subqueries, and aggregation accumulators. The LoRA model will learn
those gaps as "correct."
- **Mitigation**: filter training rows on `conversion_success` / `metadata` validity flags;
  document covered SQL subset; exclude rows with conversion warnings for the sql2nosql
  target if precision matters.

### [Medium] Train/eval leakage and split hygiene
Only one timestamped CSV exists per split. If training and evaluation draw from the same
generated file (or overlapping Spider DBs), metrics will be optimistic.
- **Mitigation**: define fixed train/validation/test CSVs; ensure `db_id` disjointness or
  at least row disjointness; seed and freeze the split.

## 2. Technical / Correctness Risks

### [High] No training infrastructure exists
There is no `Trainer`, no dataset/collator, no `peft` dependency. Everything is new code
on an untested path.
- **Mitigation**: build incrementally — dataset builder → tiny overfit test (1 batch) →
  full run. Reuse HF `Trainer`/`trl.SFTTrainer` rather than hand-rolling loops.

### [High] Causal vs seq2seq divergence
Six candidate base models span both families. LoRA `task_type`, target modules, label
masking, and the generation path all differ. A config that works for Qwen will silently
mistrain T5 (or vice versa).
- **Mitigation**: branch on `is_seq2seq_model()`; maintain per-family `target_modules`
  defaults; validate target modules exist via `model.named_modules()` before training.

### [Medium] Adapter-aware loading not implemented
`resolve_model_path()`/`CodeGenModel.load()` assume a **full** model dir (`config.json` +
weights). A LoRA checkpoint is just `adapter_config.json` + adapter weights and will fail
to load as-is.
- **Mitigation**: detect `adapter_config.json` and load via `PeftModel.from_pretrained`,
  or `merge_and_unload()` and save a merged full model for the existing path.

### [Medium] Prompt drift between training and inference
If the trainer constructs prompts differently from the runtime `PromptBuilder`s, the
fine-tuned model underperforms at eval despite low training loss.
- **Mitigation**: import and call the exact prompt builders in the dataset builder; add a
  test asserting train prompt == eval prompt for a sample.

### [Medium] Tokenization / truncation of long schemas
SQL DDL schemas are long; with `max_length=2048` and `truncation_side="left"`, the target
(SQL/Mongo/doc) at the *end* of a concatenated causal sequence can be truncated away,
producing empty/garbage labels.
- **Mitigation**: compute prompt+target lengths; truncate the *schema* region, never the
  target; log/skip examples exceeding the budget.

### [Low] Stop-string / extraction logic assumes base behavior
`SQLGenerator`/`DocumentationGenerator` post-process raw output with regex heuristics tuned
to base models. A fine-tuned model's cleaner output should still pass, but edge cases differ.
- **Mitigation**: re-validate extraction on fine-tuned outputs.

## 3. Resource / Performance Risks

- **[High] bitsandbytes / QLoRA is CUDA-only** — unavailable on the macOS/MPS dev host.
  Do not make 4-bit a hard dependency.
  - **Mitigation**: default to plain LoRA (fp16/bf16/fp32); gate QLoRA behind a CUDA check.
- **[Medium] MPS/CPU training is slow and memory-bound** — starcoder2-3b LoRA may not fit
  or will be very slow on a laptop.
  - **Mitigation**: start with 0.35–0.5B models (codegen-350M, Qwen2.5-Coder-0.5B); reserve
    3B for CUDA.
- **[Medium] Qwen doc-generation cost** to build the dataset dominates wall-clock for the
  nosql2doc track.
  - **Mitigation**: cache generated CSVs; generate docs once and reuse.
- **[Low] MPS dtype quirks** — some ops unsupported in fp16 on MPS; may need fp32.

## 4. Process / Reproducibility Risks

- **[Medium] Stale research/docs** — the prior research described FastAPI/Streamlit/
  `query_engine` that no longer exist; planning off stale docs wastes effort. (Addressed:
  these deliverables refreshed to current state.)
- **[Medium] MLflow store consistency** — `configs/default.yaml` uses
  `sqlite:///mlflow.db`; ensure training and eval log to the *same* store for comparison.
- **[Low] `.gitignore`** excludes models/data artifacts; adapters under
  `models/checkpoints/` may be ignored — confirm intended versioning/sharing strategy.

## 5. Summary of Top Risks to Address First

1. Regenerate full TEND training data (data volume). **[High]**
2. Build training infra with HF `Trainer`/`trl`; overfit-test first. **[High]**
3. Handle causal vs seq2seq branching correctly. **[High]**
4. Implement adapter-aware loading. **[Medium]**
5. Guarantee prompt parity train↔inference. **[Medium]**
