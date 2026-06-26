# Feature Plan — TENDv2 Chunked & Resumable Pipeline

> **Feature:** `tendv2-chunked-pipeline`  
> **Date:** 2026-06-24  
> **Status:** PENDING APPROVAL (see `approvals/tendv2-chunked-pipeline-approval.md`)

---

## 1. Problem

Each TENDv2 record takes ~3 seconds (Ollama codegen + judge + documentation). A full
Spider train run (~7k+ rows) or BIRD train run is hours-long and fragile: a crash
mid-run loses progress unless the partial CSV is manually recovered. Current
output paths include timestamps (`spider_train_0624_1713.csv`), which makes
resumption and automation awkward.

---

## 2. Goal

Introduce a **two-phase, resumable workflow**:

1. **One-time raw split** — pull source data, write fixed-size JSON chunks (500
   records) under stable folder paths.
2. **Chunk processing** — process one chunk file at a time into bronze CSVs with
   the **exact same columns** as today, then merge into a single combined CSV
   when all chunks are done. Re-running skips already-finished chunks.

No timestamps or version suffixes in paths or filenames.

---

## 3. Scope

### In scope

| Item | Detail |
|------|--------|
| Folder layout | `data/TENDv2/{dataset}/raw/{split}/` and `data/TENDv2/{dataset}/bronze/{split}/` |
| Datasets | Spider and BIRD |
| Splits | `train` and `test` folders (see AD-1 for split mapping) |
| Chunk size | 500 records per file (configurable, default 500) |
| Raw format | JSON array per chunk (`chunk_000.json`, `chunk_001.json`, …) |
| Bronze format | Same 11 CSV columns as `TENDv2DatasetBuilder.FIELDNAMES` |
| Resume | Skip chunks whose bronze CSV exists and row count matches raw chunk |
| Merge | **Always** concatenate bronze chunks → `{dataset}_{split}_bronze.csv` + `.summary.json` when all chunks complete (no opt-out) |
| CLI | New `split_raw` script; extend `run_tend` for chunked mode |
| Paths | Replace timestamped defaults with stable path helpers |

### Out of scope

- Changing LLM pipeline logic (codegen, judge, validators)
- Changing silver/gold tier scripts (they already accept any bronze CSV path)
- Parallel chunk processing (one chunk at a time keeps Ollama load predictable)
- Re-chunking on every run (split is one-time; re-run requires `--force` on split)

---

## 4. Architecture Decisions

### AD-1 — Split folder naming: `train` / `test`

Source loaders expose `train`, `validation` (dev), and `test`. For TENDv2 we
need gold SQL, so:

| Folder | Source split | Rationale |
|--------|--------------|-----------|
| `train/` | `train` | Full training set |
| `test/` | `validation` | Dev/validation set with gold SQL (current eval split) |

Spider/BIRD literal `test` splits (often without gold SQL) are **not** included
unless the loader returns SQL for them. This matches current usage
(`--split validation` for eval runs).

CLI `--split test` maps to folder `test` and loads source split `validation`.

### AD-2 — Data lives under `data/TENDv2/`, not the Python package

User-facing path pattern `TENDv2/spider/raw` means the logical layout under
`data/TENDv2/spider/raw/`. Keeps code (`TENDv2/*.py`) separate from artifacts.

```
data/TENDv2/
  spider/
    raw/
      train/
        chunk_000.json
        chunk_001.json
        manifest.json          # chunk count, record totals, split metadata
      test/
        chunk_000.json
        manifest.json
    bronze/
      train/
        chunk_000.csv
        chunk_001.csv
        progress.json          # resume state
      test/
        ...
    spider_train_bronze.csv    # merged output (stable name)
    spider_train_bronze.summary.json
    spider_test_bronze.csv
    spider_test_bronze.summary.json
  bird/
    (same structure)
```

### AD-3 — Raw chunk JSON schema

Each `chunk_NNN.json` is a JSON array of sample objects matching what
`SpiderSource.load_samples` / `BirdSource.load_samples` return:

```json
[
  {
    "question": "...",
    "sql": "...",
    "db_id": "...",
    "schema": "...",
    "difficulty": "..."
  }
]
```

`manifest.json` beside chunks:

```json
{
  "dataset": "spider",
  "split": "train",
  "source_split": "train",
  "chunk_size": 500,
  "total_records": 7000,
  "chunk_count": 14,
  "chunks": [
    {"file": "chunk_000.json", "records": 500, "start_index": 0},
    {"file": "chunk_001.json", "records": 500, "start_index": 500}
  ]
}
```

### AD-4 — Resume via row-count check + progress file

A chunk is **complete** when:

1. `{bronze_dir}/chunk_NNN.csv` exists, and
2. Row count (excluding header) equals `manifest.chunks[i].records`.

`progress.json` mirrors manifest for fast status display:

```json
{
  "dataset": "spider",
  "split": "train",
  "chunks_total": 14,
  "chunks_done": 8,
  "chunks_pending": ["chunk_008.json", "chunk_009.json"],
  "merged": false,
  "combined_csv": null
}
```

On startup, rebuild progress from filesystem if `progress.json` is missing
(idempotent).

Partial/corrupt CSV (row count mismatch) → reprocess that chunk (overwrite).

### AD-5 — Global index in metadata preserved

When processing chunk `k`, row `offset` within chunk gets global index
`start_index + offset` from manifest (same as today's `metadata.index`).

### AD-6 — Stable combined output names

| Artifact | Path |
|----------|------|
| Combined bronze | `data/TENDv2/{dataset}/{dataset}_{split}_bronze.csv` |
| Summary | `data/TENDv2/{dataset}/{dataset}_{split}_bronze.summary.json` |

No timestamps. Split arg `test` → filename uses `test` (e.g. `spider_test_bronze.csv`).

### AD-7 — Backward-compatible `run_tend`

- **Default (unchanged):** load all samples from source, write to `--output` or
  timestamped path (legacy; deprecate timestamp default in favor of stable path
  when `--output` omitted in chunked mode only).
- **New `--chunked` flag:** use raw/bronze chunk dirs; process pending chunks;
  **always merge** when all chunks are complete (including on resume if merge was
  skipped or combined file is missing/stale).
- **New `--merge-only` flag:** skip processing, only concatenate existing bronze
  chunks (manual recovery; normal runs never need this because merge is automatic).

### AD-8 — One-time split script

`python -m TENDv2.split_raw --dataset spider --split train [--chunk-size 500] [--force]`

- Reads from existing `SpiderSource` / `BirdSource`
- Writes chunks + manifest
- `--force` overwrites existing raw chunks
- Idempotent without `--force` (skip if manifest exists and record count matches source)

---

## 5. Execution Stages

| Stage | Work | Validation |
|-------|------|------------|
| **S1** | Extend `paths.py` with chunk/raw/bronze/combined helpers | Unit-style path tests or manual inspect |
| **S2** | Add `split_raw.py` CLI + `chunk_io.py` (read/write chunks, manifest) | Split spider validation (~1034 rows) → 3 chunks |
| **S3** | Refactor `build_tend_dataset.py` to accept sample list or chunk path | Process 1 chunk → CSV columns match current |
| **S4** | Add `chunk_runner.py` (resume, progress, merge) | Stop mid-run, restart, skips done chunks |
| **S5** | Extend `run_tend.py` CLI (`--chunked`, `--merge-only`, `--chunk-size`) | End-to-end spider test split; verify auto-merge on completion and resume |
| **S6** | Update `README.md` and deprecate timestamp path for chunked workflow | Docs review |

---

## 6. Assumptions

- 500 records/chunk is acceptable for ~25 min/chunk at 3 sec/record (serial) or
  less with existing async concurrency within a chunk.
- User runs `split_raw` once per dataset/split; raw chunks are immutable during
  processing.
- Existing `bronze_to_silver` / `silver_to_gold` scripts work unchanged against
  merged `{dataset}_{split}_bronze.csv`.
- Ollama concurrency within a chunk stays as today (`OLLAMA_CONCURRENCY`); only
  chunk-level sequencing is new.

---

## 7. Resolved decisions

| Question | Decision |
|----------|----------|
| Map `validation` → `test` folder? | Yes (AD-1) |
| Auto-merge after last chunk? | **Always merge** — mandatory when all chunks complete; no `--no-merge` flag |
| Keep timestamp paths for non-chunked runs? | Yes for backward compat; document chunked as recommended for large runs |

---

## 8. Success Criteria

- [ ] `split_raw` creates 500-record JSON chunks under `data/TENDv2/spider/raw/train/`
- [ ] `run_tend --chunked` processes chunks one at a time into matching bronze CSVs
- [ ] Interrupted run resumes without reprocessing completed chunks
- [ ] Merged `spider_test_bronze.csv` has same columns and row order as monolithic run
- [ ] No date/version strings in chunk or combined filenames
