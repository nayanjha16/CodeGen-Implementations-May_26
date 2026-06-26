# Task Breakdown — TENDv2 Chunked & Resumable Pipeline

> **Feature:** `tendv2-chunked-pipeline`  
> **Plan:** `feature-plans/tendv2-chunked-pipeline-plan.md`

---

## Task Graph

```
S1 paths.py
  └─► S2 split_raw + chunk_io
        └─► S3 build_tend_dataset refactor
              └─► S4 chunk_runner (resume + merge)
                    └─► S5 run_tend CLI
                          └─► S6 README
```

---

## S1 — Path helpers (`TENDv2/paths.py`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S1.1 | Add `get_tendv2_dataset_dir(dataset) -> data/TENDv2/{dataset}` | S | — |
| S1.2 | Add `raw_chunk_dir(dataset, split) -> .../raw/{split}` | S | S1.1 |
| S1.3 | Add `bronze_chunk_dir(dataset, split) -> .../bronze/{split}` | S | S1.1 |
| S1.4 | Add `combined_bronze_path(dataset, split) -> .../{dataset}_{split}_bronze.csv` | S | S1.1 |
| S1.5 | Add `chunk_filename(index: int) -> chunk_{index:03d}.json\|.csv` | S | — |
| S1.6 | Add `normalize_split(split) -> train\|test` (map validation/dev → test) | S | — |
| S1.7 | Add `source_split_for(folder_split) -> loader split name` | S | S1.6 |

---

## S2 — Raw split script (`TENDv2/split_raw.py`, `TENDv2/chunk_io.py`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S2.1 | `chunk_io.write_manifest(path, meta)` | S | S1 |
| S2.2 | `chunk_io.read_manifest(path)` | S | S2.1 |
| S2.3 | `chunk_io.split_samples(samples, chunk_size) -> list[list[dict]]` | S | — |
| S2.4 | `chunk_io.write_raw_chunks(dir, chunks, manifest)` | M | S2.1–S2.3 |
| S2.5 | `split_raw.py` CLI: `--dataset`, `--split`, `--chunk-size`, `--force` | M | S2.4 |
| S2.6 | Load samples via existing `SpiderSource` / `BirdSource` + `source_split_for` | S | S1.7, S2.5 |
| S2.7 | Skip if manifest exists and total_records matches (unless `--force`) | S | S2.5 |

**Acceptance:** `python -m TENDv2.split_raw --dataset spider --split test` creates
`data/TENDv2/spider/raw/test/chunk_*.json` + `manifest.json`.

---

## S3 — Builder refactor (`TENDv2/build_tend_dataset.py`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S3.1 | Add `build_chunk_async(samples, output_path, start_index=0)` | M | — |
| S3.2 | Accept optional `samples: list[dict]` instead of always calling `_load_samples()` | S | S3.1 |
| S3.3 | Use `start_index + offset` for `metadata.index` | S | S3.1 |
| S3.4 | Keep existing `build_async()` for non-chunked (loads from source) | S | S3.2 |

**Acceptance:** Single chunk CSV has identical columns/structure to current output.

---

## S4 — Chunk orchestration (`TENDv2/chunk_runner.py`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S4.1 | `list_pending_chunks(manifest, bronze_dir) -> list[str]` via row-count check | M | S2 |
| S4.2 | `update_progress(progress_path, ...)` read/write | S | S4.1 |
| S4.3 | `rebuild_progress_from_disk(manifest, bronze_dir)` | M | S4.1 |
| S4.4 | `process_pending_chunks(builder, manifest, bronze_dir)` loop one chunk at a time | M | S3, S4.1 |
| S4.5 | `merge_bronze_chunks(manifest, bronze_dir, combined_path)` ordered concat | M | S2 |
| S4.6 | Write combined `.summary.json` via existing `summarize_csv` | S | S4.5 |
| S4.7 | `run_chunked_pipeline(dataset, split, **builder_kwargs)` top-level API | M | S4.4–S4.6 |
| S4.8 | After all chunks done (or on resume when all done), **always** call merge | S | S4.5 |

**Acceptance:** Kill after chunk 2; rerun completes 3..N only; merge row count = manifest.total_records. Final run always writes combined CSV + summary.

---

## S5 — CLI updates (`TENDv2/run_tend.py`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S5.1 | Add `--chunked` flag | S | S4 |
| S5.2 | Add `--merge-only` flag | S | S4 |
| S5.3 | Add `--chunk-size` (pass-through to split_raw hint in error message) | S | — |
| S5.4 | Chunked mode: error if raw manifest missing (prompt to run split_raw) | S | S5.1 |
| S5.5 | Print progress summary on start/end (chunks done/pending); log merge path on completion | S | S4 |

**Acceptance:**

```bash
python -m TENDv2.split_raw --dataset spider --split test
python -m TENDv2.run_tend --dataset spider --split test --chunked
# → data/TENDv2/spider/spider_test_bronze.csv
```

---

## S6 — Documentation (`TENDv2/README.md`)

| ID | Task | Complexity | Depends |
|----|------|------------|---------|
| S6.1 | Document folder layout and workflow | S | S5 |
| S6.2 | Document resume behavior and `--force` on split | S | S5 |
| S6.3 | Mark timestamp paths as legacy for large runs | S | S5 |

---

## Complexity Legend

| Label | Meaning |
|-------|---------|
| S | Small (~30 min) |
| M | Medium (~1–2 hr) |

**Estimated total:** ~1–2 days implementation + smoke test on spider test split.
