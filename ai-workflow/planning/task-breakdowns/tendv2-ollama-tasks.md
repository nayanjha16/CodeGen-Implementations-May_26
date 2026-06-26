# Task Breakdown — TENDv2 (Ollama)

> **Feature:** `tendv2-ollama` · **Date:** 2026-06-24

Complexity: S (small), M (medium), L (large).

## Stage 1 — Ollama client util

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T1.1 | `src/llm/__init__.py` | — | S |
| T1.2 | `OllamaClient` sync `chat()` over `/api/chat` (`stream:false`) | T1.1 | M |
| T1.3 | `AsyncOllamaClient.chat()` with `httpx.AsyncClient` + semaphore | T1.2 | M |
| T1.4 | JSON-mode (`format:"json"`), `think:false`, options (temp, num_ctx) | T1.2 | S |
| T1.5 | Retries with backoff + timeout + clear errors | T1.3 | M |
| T1.6 | Env config helpers (base url, models, concurrency, timeout) | T1.2 | S |

## Stage 2 — Codegen + judge

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T2.1 | `prompts.py` — combined codegen prompt (schema+query+doc JSON) | — | M |
| T2.2 | `prompts.py` — per-field fallback prompts | T2.1 | S |
| T2.3 | `prompts.py` — judge prompt (equivalence JSON) | — | M |
| T2.4 | `code_generator.py` — async generate, parse, validate, fallback | T1.*, T2.1-2 | L |
| T2.5 | `judge.py` — async evaluate, parse JSON, strip think | T1.*, T2.3 | M |

## Stage 3 — Sources, paths, reuse

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T3.1 | `paths.py` — `data/TENDv2` + timestamped CSV name | — | S |
| T3.2 | `spider_source.py` — Spider split loader (v1 pattern) | — | S |
| T3.3 | `schema_to_sql.py` — re-export v1 generator | — | S |
| T3.4 | `validator.py` — structural checks (reuse/port) | — | S |

## Stage 4 — Async pipeline + CLI

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T4.1 | `build_tend_dataset.py` — per-row async coroutine | T2.*, T3.* | L |
| T4.2 | Bounded-concurrency gather + ordered incremental CSV writer | T4.1 | L |
| T4.3 | `summarize_csv()` (+ `.summary.json`) | T4.1 | S |
| T4.4 | `run_tend.py` — argparse CLI + asyncio entrypoint | T4.1-3 | M |
| T4.5 | `__init__.py` + `README.md` | T4.* | S |

## Stage 5 — BIRD

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T5.1 | `bird_source.py` wrapping `BirdLoader.load_split` | T4.* | M |
| T5.2 | CLI `--dataset bird` wiring | T5.1 | S |

## Stage 6 — Deps, env, smoke

| ID | Task | Deps | Complexity |
|----|------|------|------------|
| T6.1 | Add `httpx` to `requirements.txt` | — | S |
| T6.2 | Add Ollama vars to `.env.example` | — | S |
| T6.3 | Lint + import smoke + CLI `--help` | all | S |
