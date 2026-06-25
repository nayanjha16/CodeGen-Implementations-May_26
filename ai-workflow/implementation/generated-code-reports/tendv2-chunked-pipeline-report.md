# Generated Code Report — TENDv2 Chunked Pipeline

> **Feature:** `tendv2-chunked-pipeline`  
> **Date:** 2026-06-24

## Files created

- `TENDv2/chunk_io.py` — manifest, raw chunk I/O, pending detection, merge
- `TENDv2/split_raw.py` — one-time CLI to export 500-record JSON chunks
- `TENDv2/chunk_runner.py` — resumable processing orchestrator + auto-merge

## Files modified

- `TENDv2/paths.py` — stable paths, split normalization
- `TENDv2/build_tend_dataset.py` — `_write_samples_async`, `build_chunk_async`
- `TENDv2/run_tend.py` — `--chunked`, `--merge-only`, `--chunk-size`
- `TENDv2/README.md` — chunked workflow documentation

## Validation status

| Check | Result |
|-------|--------|
| `split_raw` spider/test | PASS — 3 chunks, 1034 records |
| Idempotent re-run | PASS |
| Merge-only (mock bronze) | PASS — 1034 combined rows |
| Linter | PASS — no errors |

## API changes

```bash
# New
python -m TENDv2.split_raw --dataset spider --split train [--chunk-size 500] [--force]
python -m TENDv2.run_tend --dataset spider --split test --chunked
python -m TENDv2.run_tend --dataset spider --split test --chunked --merge-only
```

Combined output: `data/TENDv2/{dataset}/{dataset}_{split}_bronze.csv`
