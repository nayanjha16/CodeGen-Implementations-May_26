# Dependency Analysis — TENDv2 Chunked Pipeline

> **Feature:** `tendv2-chunked-pipeline`

---

## Internal Module Dependencies

```
src/datasets/spider_loader.py ──► TENDv2/spider_source.py ──► split_raw.py
src/datasets/bird_loader.py   ──► TENDv2/bird_source.py   ──► split_raw.py

TENDv2/paths.py ──► chunk_io.py ──► split_raw.py
                              └──► chunk_runner.py ──► run_tend.py

TENDv2/build_tend_dataset.py ◄── chunk_runner.py
  ├── code_generator.py
  ├── judge.py
  ├── validator.py
  └── src/llm/ollama_client.py

TENDv2/bronze_to_silver.py  ◄── merged {dataset}_{split}_bronze.csv (no code change)
TENDv2/silver_to_gold.py      ◄── silver output (no code change)
```

---

## Ordering Constraints

1. **`paths.py` before all new modules** — every path reference goes through helpers.
2. **`chunk_io.py` before `split_raw.py` and `chunk_runner.py`** — shared manifest/chunk logic.
3. **`build_tend_dataset.py` refactor before `chunk_runner.py`** — runner calls chunk build API.
4. **`split_raw` before `run_tend --chunked`** — raw manifest must exist on disk.
5. **Merge after all bronze chunks** — depends on complete bronze chunk set.

---

## External Dependencies

| Dependency | Usage | Change needed |
|------------|-------|---------------|
| Ollama daemon | LLM calls per record | None |
| Spider/BIRD cached data | `SpiderLoader` / `BirdLoader` | None (downloads already in progress) |
| `tqdm` | Progress bar | None |
| stdlib `json`, `csv`, `pathlib` | Chunk I/O | None |

---

## Files to Create

| File | Purpose |
|------|---------|
| `TENDv2/chunk_io.py` | Manifest, chunk read/write, split logic |
| `TENDv2/split_raw.py` | One-time raw chunking CLI |
| `TENDv2/chunk_runner.py` | Resume, progress, merge orchestration |

---

## Files to Modify

| File | Change |
|------|--------|
| `TENDv2/paths.py` | Stable path helpers; split normalization |
| `TENDv2/build_tend_dataset.py` | Chunk-aware build API |
| `TENDv2/run_tend.py` | `--chunked`, `--merge-only` (merge always runs when chunks complete) |
| `TENDv2/README.md` | New workflow docs |

---

## Files Unchanged

- `TENDv2/code_generator.py`, `judge.py`, `validator.py`, `prompts.py`
- `TENDv2/bronze_to_silver.py`, `silver_to_gold.py`
- `src/llm/ollama_client.py`

---

## Data Dependencies

| Prerequisite | Command |
|--------------|---------|
| Spider dataset cached | `SpiderLoader().download()` |
| BIRD dataset cached | `BirdLoader().download()` |

Split script fails fast with a clear message if source JSON is missing.
