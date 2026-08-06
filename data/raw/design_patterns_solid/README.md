# Design Patterns + SOLID Parallel Dataset

ClassEval-style **Java ↔ Python** teaching corpus for GoF design patterns and SOLID principles.

| Split | Records | Domains |
|---|---|---|
| **train** | 1,500 | 40 train-only domains |
| **test** | 200 | 8 held-out domains (disjoint) |

Total: **1,700** parallel pairs (within the 1k–2k target).

## Layout

```text
design_patterns_solid/
  README.md
  manifest_train.jsonl
  manifest_test.jsonl
  split.json
  Java -> generated/java
  Python -> generated/python
  generated/
    java/solution/{id}.java
    java/test/{id}Test.java
    python/solution/{id}.py
    python/test/test_{id}.py
```

Each manifest row:

```json
{
  "id": "strategy_payments_minimal",
  "category": "behavioral",
  "pattern_or_principle": "strategy",
  "kind": "design_pattern",
  "domain": "payments",
  "java_path": "generated/java/solution/....java",
  "python_path": "generated/python/solution/....py",
  "split": "train"
}
```

`kind` ∈ `design_pattern | solid | combo`.

## Coverage

- **23 GoF patterns** (same labels as `agent/prompts.py` `KNOWN_PATTERNS`)
- **5 SOLID principles:** `srp`, `ocp`, `lsp`, `isp`, `dip`
- **5 combo** scenarios (e.g. `strategy+ocp`, `factory+dip`)
- **Tiers:** `minimal`, `logging`, `errors` (domain-specific class names)
- **Test set:** every SOLID principle ≥ 5 examples; pattern labels spread across held-out domains  
  (`wallet`, `ticket`, `booking`, `review`, `feed`, `comment`, `profile`, `license`)

No AVATAR / ClassEval IDs are mixed into this corpus.

Default seed `42` label totals (train+test), from `split.json`:

| Label | Count | Label | Count |
|---|---:|---|---:|
| singleton | 69 | bridge | 63 |
| template method | 60 | command / decorator / flyweight / isp | 59 each |
| interpreter / lsp | 57 | composite / mediator / ocp | 53 |
| proxy | 52 | factory+dip | 51 |
| adapter+isp / factory / observer / srp / strategy | 50 | abstract factory / observer+srp / state / strategy+ocp / visitor | 49 |
| adapter | 48 | builder / chain of responsibility / facade | 47 |
| memento | 46 | decorator+ocp / dip / prototype | 43 |
| iterator | 37 | | |

Exact numbers: see `split.json` → `counts_by_label`.

## Regenerate

From the repo root (use project venv):

```bash
# Generate raw corpus (default 1500 train / 200 test)
.venv/bin/python data/scripts/patterns/generate_dataset.py \
  --target-train 1500 --target-test 200 --seed 42

# Toward the upper end of 1k–2k
.venv/bin/python data/scripts/patterns/generate_dataset.py \
  --target-train 1800 --target-test 250 --seed 42

# Validate manifests / files / domain disjointness
.venv/bin/python data/scripts/patterns/validate_pairs.py

# Build HuggingFace datasets for fine-tuning
.venv/bin/python data/scripts/preprocess_design_patterns.py
```

Processed output:

- `data/processed/java2py_patterns/train`
- `data/processed/java2py_patterns/test` (also copied to `val/`)

## Generators

Templates and expansion live in code (not Jinja files):

- [`data/scripts/patterns/define_catalog.py`](../../scripts/patterns/define_catalog.py) — patterns, SOLID, domains, split
- [`data/scripts/patterns/code_templates.py`](../../scripts/patterns/code_templates.py) — Java/Python renderers
- [`data/scripts/patterns/generate_dataset.py`](../../scripts/patterns/generate_dataset.py) — expansion + manifests
- [`data/scripts/patterns/validate_pairs.py`](../../scripts/patterns/validate_pairs.py) — validation
- [`data/scripts/preprocess_design_patterns.py`](../../scripts/preprocess_design_patterns.py) — HF export

## Fine-tuning note

Point a Java→Python LoRA config at `data/processed/java2py_patterns` for a **patterns-only** run, or merge with AVATAR/ClassEval in a later combined preprocess step. Keep this corpus separate for ablation.

## License

Original generated teaching examples for this project (same license as the repository). Not scraped from copyrighted pattern catalogs.
