# Approval — TENDv2 Chunked & Resumable Pipeline

> **Feature:** `tendv2-chunked-pipeline`  
> **Status:** PENDING

---

## Proposed Scope (for approval)

1. Raw data split into 500-record JSON chunks under `data/TENDv2/{dataset}/raw/{train|test}/`
2. Resumable chunk-by-chunk bronze CSV generation (same 11 columns as today)
3. Stable merged output: `data/TENDv2/{dataset}/{dataset}_{split}_bronze.csv` (no timestamps)
4. One-time `split_raw` script + extended `run_tend --chunked` CLI
5. Map source `validation`/`dev` split → folder name `test`

## Out of scope

- LLM pipeline changes
- Silver/gold script changes
- Parallel multi-chunk processing

## Revision history

| Date | Change |
|------|--------|
| 2026-06-24 | Initial plan created |
| 2026-06-24 | **Always merge** when all chunks complete (no `--no-merge`) |

## Approval

- [x] Scope approved — ready for implementation
- [ ] Scope revised — see notes below

**Notes:**

Implemented 2026-06-24 per user request. Always merge when all chunks complete.
