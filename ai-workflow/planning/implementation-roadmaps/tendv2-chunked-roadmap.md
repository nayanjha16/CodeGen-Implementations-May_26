# Implementation Roadmap — TENDv2 Chunked Pipeline

> **Feature:** `tendv2-chunked-pipeline`  
> **Plan:** `feature-plans/tendv2-chunked-pipeline-plan.md`

---

## Milestones

| # | Milestone | Exit criteria |
|---|-----------|---------------|
| M1 | Path + I/O foundation | Stable paths resolve; manifest read/write works |
| M2 | Raw split complete | Spider + BIRD train/test chunks on disk |
| M3 | Single-chunk processing | One chunk → bronze CSV matches current schema |
| M4 | Resume + merge | Full test split end-to-end with simulated interrupt |
| M5 | Docs + handoff | README updated; approval signed |

---

## Implementation Order

### Phase 1 — Foundation (M1)

1. Extend `TENDv2/paths.py` (S1)
2. Create `TENDv2/chunk_io.py` (S2.1–S2.4)

**Checkpoint:** Run path helpers in a shell snippet; write/read a dummy manifest.

### Phase 2 — One-time split (M2)

3. Create `TENDv2/split_raw.py` (S2.5–S2.7)
4. Run for both datasets:

```bash
python -m TENDv2.split_raw --dataset spider --split train
python -m TENDv2.split_raw --dataset spider --split test
python -m TENDv2.split_raw --dataset bird --split train
python -m TENDv2.split_raw --dataset bird --split test
```

**Checkpoint:** Verify chunk counts: `ceil(total/500)` files per split; manifest totals match loader.

### Phase 3 — Chunk builder (M3)

5. Refactor `build_tend_dataset.py` for chunk input (S3)
6. Manual test: process `chunk_000.json` only with small `--max-samples` equivalent

**Checkpoint:** Diff CSV header + sample row against existing `spider_validation_bronze.csv` format.

### Phase 4 — Orchestration (M4)

7. Create `TENDv2/chunk_runner.py` (S4)
8. Extend `run_tend.py` CLI (S5)
9. Integration test on spider test split (~1034 rows → 3 chunks):

```bash
# Process chunk 0 only (temporary max-chunks flag or manual rename test)
python -m TENDv2.run_tend --dataset spider --split test --chunked
# Interrupt after chunk 1 (Ctrl+C)
python -m TENDv2.run_tend --dataset spider --split test --chunked  # resumes
```

**Checkpoint:** Combined CSV row count = 1034; resume skipped completed chunks.

### Phase 5 — Polish (M5)

10. Update README (S6)
11. Update workflow context files
12. User approval sign-off

---

## Testing Checkpoints

| Test | Command | Expected |
|------|---------|----------|
| Split idempotency | Run `split_raw` twice | Second run no-op |
| Split force | `split_raw --force` | Overwrites chunks |
| Resume | Interrupt + rerun `--chunked` | Skips done chunks |
| Corrupt chunk | Truncate a bronze CSV | Reprocesses that chunk |
| Merge only | `--merge-only` after all chunks done | Combined CSV + summary |
| Column parity | Compare headers | Same 11 columns as `FIELDNAMES` |
| Silver tier | `bronze_to_silver` on merged file | Works unchanged |

---

## Rollout Notes

- Existing timestamped CSV workflow remains for quick small runs (`--max-samples 5`).
- Large production runs should use: `split_raw` once → `run_tend --chunked` (repeat until done).
- Raw chunks are source-of-truth; do not edit bronze chunks manually during a run.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Ctrl+C mid-chunk leaves partial CSV | Row-count check treats mismatch as incomplete → reprocess |
| Disk space for duplicate raw + bronze | Raw JSON is small vs CSV; document cleanup policy |
| Index gaps after reprocess | Always rewrite full chunk CSV on reprocess |
| validation vs test naming confusion | Document in README; CLI accepts both `--split test` and `--split validation` |
