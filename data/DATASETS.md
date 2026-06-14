# Dataset Reference (Spider & BIRD)

Local paths, raw JSON fields, loader output, and difficulty/complexity labels.

Loaders: `src/datasets/spider_loader.py`, `src/datasets/bird_loader.py`

---

## Spider

**Location:** `data/spider/spider-master/evaluation_examples/examples/`

| File | Count | Purpose |
|------|-------|---------|
| `dev.json` | 1,034 | Validation (dev) split |
| `train_spider.json` | 7,000 | Training split |
| `tables.json` | 166 DBs | Schema metadata |

> This repo caches the Spider **evaluation examples** subset. The full `spider_data/` bundle (with SQLite databases) is downloaded on first use via `SpiderLoader` if not present.

### Per-example fields (`dev.json`, `train_spider.json`)

| Field | Type | Description |
|-------|------|-------------|
| `db_id` | string | Database identifier |
| `question` | string | Natural-language question |
| `question_toks` | list | Tokenized question |
| `query` | string | Gold SQL |
| `query_toks` | list | Tokenized SQL |
| `query_toks_no_value` | list | SQL tokens with literals replaced |
| `sql` | dict | Structured SQL parse tree (select, from, where, groupBy, orderBy, etc.) |

### Schema fields (`tables.json`)

| Field | Description |
|-------|-------------|
| `db_id` | Database id |
| `table_names` / `table_names_original` | Table names |
| `column_names` / `column_names_original` | `[table_idx, column_name]` pairs |
| `column_types` | Column types |
| `primary_keys` | Primary key column indices |
| `foreign_keys` | Foreign-key column index pairs |

### Difficulty / complexity

**Spider has no official difficulty field.** There is no `difficulty`, `level`, or `complexity` key in the raw JSON.

`SpiderLoader` standardizes each example to:

```json
{"question": "...", "schema": "...", "sql": "...", "db_id": "..."}
```

To bucket by complexity, derive it from the `sql` structure or SQL heuristics (joins, aggregations, subqueries, etc.).

---

## BIRD (BirdBench)

**Location:** `data/bird/bird_data/`

| File | Count | Purpose |
|------|-------|---------|
| `dev.json` | 1,534 | Dev / validation split |
| `dev_tied_append.json` | 42 | Extra tied-result questions |
| `dev_tables.json` | 11 DBs | Schema metadata |
| `dev_databases/` | — | SQLite databases per `db_id` |

### Per-example fields (`dev.json`)

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | int | Unique question id |
| `db_id` | string | Database identifier |
| `question` | string | Natural-language question |
| `evidence` | string | Domain hints / formulas needed to answer |
| `SQL` | string | Gold SQL (capital `SQL` in raw JSON) |
| `difficulty` | string | **Official difficulty label** |

### Schema fields (`dev_tables.json`)

Same structure as Spider `tables.json` (`db_id`, table/column names, types, primary keys, foreign keys).

### Difficulty labels

BIRD uses three official values (not easy/medium/hard):

| Label | Dev count | Rough mapping |
|-------|-----------|---------------|
| `simple` | 925 | Easy |
| `moderate` | 464 | Medium |
| `challenging` | 145 | Hard / complex |

`BirdLoader` standardizes each example to:

```json
{"question": "...", "schema": "...", "sql": "...", "db_id": "...", "difficulty": "simple"}
```

`schema` is built from `db_id` + `evidence`, not from `dev_tables.json`.

Example:

```python
from src.datasets.bird_loader import BirdLoader

examples = BirdLoader().load_split("validation")
easy = [e for e in examples if e["difficulty"] == "simple"]
medium = [e for e in examples if e["difficulty"] == "moderate"]
hard = [e for e in examples if e["difficulty"] == "challenging"]
```

---

## TEND outputs (`data/TEND/`)

Derived CSVs from the TEND pipeline (not raw Spider/BIRD JSON).

Columns: `source`, `db_id`, `question`, `sql_schema`, `sql_query`, `nosql_schema`, `nosql_query`, `metadata`, `conversion_success`, `schema_correct`, `query_correct`, `overall_correct`, `schema_reason`, `query_reason`, `evaluation_response`

The `metadata` JSON includes structural hints (`joins`, `aggregations`, `from_clauses`, `tables`) but **no** simple/medium/hard label.

---

## Quick comparison

| Dataset | Official difficulty? | Field | Values |
|---------|------------------------|-------|--------|
| Spider | No | — | — |
| BIRD | Yes | `difficulty` | `simple`, `moderate`, `challenging` |
