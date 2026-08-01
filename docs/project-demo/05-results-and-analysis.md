# Results & Analysis

Baseline vs LoRA comparison on the Spider gold validation benchmark (50 examples). **Production numbers use LoRA v3** with TEND Postgres/Mongo execution enabled.

**Source of truth:** [../reference/version-tracker.md](../reference/version-tracker.md)

---

## 1. Experimental Setup (v3 production eval)

| Parameter | Value |
|-----------|-------|
| Base model | `Salesforce/codegen-350M-multi` |
| Production adapters | LoRA **v3** — r=32, alpha=64, attn + FFN, **10 epochs**, full TEND (~8k/task) |
| Evaluation dataset | `spider_gold_validation` (50 examples) |
| Execution | **TEND Docker** Postgres + Mongo (`database_execution: true`) |
| Documentation judge | Ollama **`gemma3:4b`** (score 0–10) |
| Decoding | Greedy |

### Compared runs (primary)

| Run | Results path |
|-----|--------------|
| Baseline v3 | `results/spider_gold_validation_codegen-350M-multi_baseline-v3/` |
| LoRA v2 | `results/spider_gold_validation_codegen-350M-multi_lora-v2/` |
| **LoRA v3 (prod)** | `results/spider_gold_validation_codegen-350M-multi_lora-v3/` |

---

## 2. Headline Summary (v3 vs baseline)

| Task | Metric | Baseline | LoRA v2 | **LoRA v3** |
|------|--------|----------|---------|-------------|
| Text2SQL | Execution accuracy | 14% | 60% | **66%** |
| SQL2NoSQL | Execution accuracy | 22% | 74% | **86%** |
| Documentation | Judge score /10 | 8.33 | 8.41 | **8.82** |

**Exact match (v3):** text2sql 48%, sql2nosql 78%. **Structural similarity (v3):** text2sql 0.95, sql2nosql 0.98.

LoRA v3 **outperforms baseline on every primary metric** and improves on v2 mainly via wider LoRA (r=32 + FFN) and **10 epochs** vs v2’s 5.

---

## 3. Version Progression

| Version | Train | LoRA | Epochs | Text2SQL exec | SQL2NoSQL exec | Doc judge |
|---------|-------|------|--------|---------------|----------------|-----------|
| Baseline | — | — | — | 14% | 22% | 8.33 |
| v1 (smoke) | 50 rows | r=16 attn | 10 | pipeline check | pipeline check | smoke only |
| v2 | full TEND | r=16 attn | **5** | 60% | 74% | 8.41 |
| **v3 (prod)** | full TEND | r=32 + FFN | **10** | **66%** | **86%** | **8.82** |

**v2 vs v3:** same training scale (~8k rows/task); v3 adds LoRA capacity and longer training schedule.

Reports:
- [baseline-vs-lora-v2-comparison.md](../../results/spider_gold_validation_codegen-350M-multi_lora-v2/baseline-vs-lora-v2-comparison.md)
- [lora-v1-v3-vs-baseline-comparison.pptx](../reference/lora-v1-v3-vs-baseline-comparison.pptx)

---

## 4. LoRA v1 (Historical Smoke Run)

Early smoke run (50 training rows, 10 epochs) proved the pipeline before full TEND training. Metrics used semantic judge heavily; execution was not the primary gate at that stage.

See `results/spider_gold_validation_codegen-350M-multi_lora-v1/` and `..._lora-v1_50samples/` for archived CSVs.

---

## 5. Key Findings

### What worked

1. **LoRA fine-tuning helps at every scale** — smoke (v1) → full TEND (v2/v3)
2. **Execution accuracy is the right capstone metric** — 14% → 66% text2sql, 22% → 86% sql2nosql with TEND Docker
3. **LoRA capacity matters at full scale** — v3 beats v2 with same data (r=32 + FFN, 10 epochs)
4. **Independent task design validated** — each adapter improves its task in isolation

### Remaining gaps

1. Complex multi-table joins still fail execution on some gold examples
2. Documentation judge gains are modest (+0.49) vs large execution jumps on code tasks
3. Cloud Run cold start adds latency for live demos

---

## 6. Limitations

| Limitation | Mitigation |
|------------|------------|
| 350M parameter ceiling | Acceptable for capstone; LoRA still shows large gains |
| Frozen 50-example benchmark | Fast and fair; use `--full-split` for extended analysis |
| Agent schema tool (keywords) | Documented; embedding retrieval is future work |

---

## 7. Artifact References

| Artifact | Location |
|----------|----------|
| Baseline v3 metrics | `results/..._baseline-v3/metrics.json` |
| LoRA v2 metrics | `results/..._lora-v2/metrics.json` |
| LoRA v3 metrics | `results/..._lora-v3/metrics.json` |
| Version tracker | [../reference/version-tracker.md](../reference/version-tracker.md) |
| Per-sample CSVs | `text2sql_details.csv`, `sql2nosql_details.csv`, `documentation_details.csv` |
