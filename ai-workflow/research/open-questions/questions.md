# Open Questions — CodeGen Studio

Questions to resolve before planning/implementation. Grouped by theme; each notes why it
matters and the current code-based assumption.

## 1. Project Scope & Goals

1. **Is fine-tuning in scope?** `scripts/train.sh` is an explicit placeholder. Is the goal
   to (a) stay a baseline/eval/demo, or (b) add a real training loop on Spider/BIRD?
   *Impacts: dataset prep, GPU requirements, new modules.*
2. **Is this primarily a teaching/demo artifact or a product?** The IIT Hyderabad demo
   script and narrated output suggest education. Production hardening (auth, scaling) is
   only worthwhile under the product framing.
3. **What does "done" look like for the NoSQL track?** Is string generation sufficient, or
   is real MongoDB execution + execution-accuracy expected?

## 2. Business Logic Ambiguities

4. **Execution accuracy when no DBs are present** — `evaluate_all` only computes execution
   accuracy when `db_paths` are provided; otherwise it is silently absent. Should missing
   DBs be an error, a warning, or a logged skip?
5. **Reference SQL source for Spider** — `_standardize` uses `query` then falls back to
   `sql`. Spider's `sql` field is a structured dict, not text. Is the text `query` field
   always the intended gold reference?
6. **BIRD schema is evidence-only** — BIRD examples carry `db_id` + `evidence` as the
   "schema" (no column listing). Is that intentional for prompting, or should full table
   schemas be loaded for BIRD like Spider?
7. **GROUP BY semantics in NoSQL** — should aggregation produce accumulators
   (`$sum`/`$avg`/count) inferred from SELECT, or is grouping-by-key alone acceptable?

## 3. Unclear / Inconsistent APIs

8. **`/interactive-query` parameter style** — should it accept a JSON body (like the other
   POST endpoints) instead of query params? Current behavior is inconsistent.
9. **`GenerateSQLRequest.schema` field name** — acceptable to rename (e.g. `db_schema`)
   given it shadows Pydantic's `BaseModel.schema()`? Any external clients depending on the
   `schema` key?
10. **MLflow backend store of record** — config (`sqlite:///mlflow.db`), demo
    (`mlruns/` directory), and compose (`/mlruns` file store) disagree. Which is canonical?
11. **Decoding strategy default** — config sets `decoding_strategy: greedy` with
    `num_beams: 4`; beam is only used if explicitly selected. Is greedy the intended default
    for reported baselines?

## 4. Data & Environment

12. **Spider full-data download** — the gdown Google Drive mirror is unpinned and `gdown`
    is undeclared. What is the supported, reproducible way to obtain Spider databases?
13. **Local `datasets/` vs HF `datasets`** — is the HF `datasets` dependency actually used
    anywhere? If not, can the dependency be dropped to avoid the name shadow?
14. **Target hardware** — CPU-only acceptable for baselines, or is CUDA assumed? Affects
    timeouts, batch sizes, and which metrics (BERTScore) are practical.
15. **Offline operation** — must the system run without network (pre-staged model/dataset
    caches), or is download-on-first-run acceptable?

## 5. Edge Cases

16. **Multi-line / multi-statement generated SQL** — how should `_extract_sql` handle
    outputs with multiple statements or SQL spanning several lines?
17. **WHERE with OR / IN / LIKE / BETWEEN** — the regex fallback only handles `AND`-joined
    simple comparisons. Are these constructs required for the target queries?
18. **Empty / non-SELECT model output** — current behavior returns the first non-empty line
    as "SQL". Should non-SQL output be flagged/rejected instead?
19. **Result-set comparison with NULLs / unhashable types** — `_normalize_rows` sorts on
    `row.items()`; mixed types or `None` ordering could raise or misrank. Tolerance needed?
20. **Concurrency** — is the model expected to serve concurrent requests? It is not
    thread-safe as written; do we need a queue/worker model?

## 6. Quality Gates

21. **Required test coverage threshold** — README mentions coverage targets but no minimum
    is enforced. What coverage gate (if any) should CI enforce?
22. **Is an integration test against the real model desired**, or is full mocking the
    intended testing strategy (for speed/CI)?
23. **Expected baseline metric ranges** — are there target numbers the 350M baseline should
    reproduce (for regression detection), or is the harness purely exploratory?
