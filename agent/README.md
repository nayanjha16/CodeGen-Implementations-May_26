# AI Database Agent

Standalone capstone agent per **[doc/agent.md](doc/agent.md)** — full spec (§1–§12).

Orchestrates three MCP tools; **never generates SQL directly**. Generative work is done by **CodeGen + LoRA v3** on Cloud Run via HTTP.

| Resource | Link |
| --- | --- |
| Spec | [doc/agent.md](doc/agent.md) |
| Planning | [database-agent-plan.md](../ai-workflow/planning/feature-plans/database-agent-plan.md) |
| Eval / deploy | [evaluation-and-deploy-runbook.md](../docs/evaluation-and-deploy-runbook.md) |
| Project overview | [README.md](../README.md) |

## Folder layout

```text
agent/
├── main.py                          # CLI entry point
├── web/                             # FastAPI chat UI (Stage 10)
│   ├── app.py
│   ├── templates/index.html
│   └── static/css|js/
├── orchestration/                   # LangGraph pipeline + execution
│   ├── graph.py
│   ├── runner.py
│   └── state.py
├── orchestrator/                    # Intent, planning, prompts, retry
│   ├── intent_detector.py
│   ├── planner.py
│   ├── prompts.py
│   └── retry.py
├── config/settings.py               # loads agent/.env only
├── clients/                         # CodeGen HTTP + Ollama orchestrator
├── tools/                           # schema, CodeGen, execution
├── database/                        # Postgres, Mongo, profiles
├── lib/                             # SQL validation, src imports
├── mcp/                             # stdio MCP server
├── scripts/                         # setup, mirror, verify, integration runner
├── tests/
├── data/standalone/chinook|northwind/   # demo SQL dumps + questions
├── doc/agent.md                     # specification
├── .env.example                     # copy → .env (single config file)
└── requirements.txt
```

## Prerequisites

| Service | Purpose |
| --- | --- |
| **TEND Docker** | Postgres + Mongo with Chinook (and optionally Northwind) loaded |
| **CodeGen API** | Cloud Run — text2sql / sql2nosql / nosql2doc generation |
| **Ollama** | Local orchestrator — intent fallback, summaries, SQL explanations (`gemma3:4b`) |

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
Copy-Item agent\.env.example agent\.env   # if not already done
pip install -r agent\requirements.txt      # langgraph, httpx, psycopg, mcp, …
$env:PYTHONPATH = (Get-Location).Path
python agent\scripts\verify_demo_databases.py
```

## Quick start — test all three tasks (multi-table)

Demo questions live in **[data/standalone/chinook/questions.txt](data/standalone/chinook/questions.txt)** — section **CAPSTONE DEMO SET** (all multi-table joins).

Each task expects a **different input type**:

| Task | Input | Multi-table example |
| --- | --- | --- |
| **text2sql** | Natural language question | `"List the top 5 tracks by unit price with album title and artist name."` |
| **sql2nosql** | **SQL with JOINs** | Artist + Album + Track query (see below) |
| **nosql2doc** | Mongo query or doc request | Document a join SQL or aggregation pipeline |

Chinook uses **quoted PascalCase** table names (`"Customer"`, `"Artist"`, …). Mongo collections are lowercase (`customer`, `artist`, …).

### 1. text2sql (multi-table)

```powershell
$env:PYTHONPATH = (Get-Location).Path

# 3 tables: Track + Album + Artist
python -m agent.main "List the top 5 tracks by unit price with album title and artist name."

# 2 tables: Customer + Invoice
python -m agent.main "Which customer has the highest total spending?"

# 2 tables: Genre + Track
python -m agent.main "How many tracks are in each genre?"
```

### 2. sql2nosql (multi-table JOINs)

Copy SQL from [questions.txt](data/standalone/chinook/questions.txt) section **SQL2NOSQL — Multi-table SQL**:

```powershell
# 2 tables: artist album counts
python -m agent.main --intent sql2nosql --sql 'SELECT ar."Name" AS artist, COUNT(al."AlbumId") AS album_count FROM "Artist" ar JOIN "Album" al ON ar."ArtistId" = al."ArtistId" GROUP BY ar."Name" ORDER BY album_count DESC LIMIT 5;'

# 3 tables: track + album + artist
python -m agent.main --intent sql2nosql --sql 'SELECT ar."Name" AS artist, al."Title" AS album, t."Name" AS track, t."UnitPrice" FROM "Track" t JOIN "Album" al ON t."AlbumId" = al."AlbumId" JOIN "Artist" ar ON al."ArtistId" = ar."ArtistId" ORDER BY t."UnitPrice" DESC LIMIT 5;'

# 4 tables: invoice lines with track and customer
python -m agent.main --intent sql2nosql --sql 'SELECT c."FirstName", c."LastName", t."Name" AS track, il."Quantity", il."UnitPrice" FROM "InvoiceLine" il JOIN "Track" t ON il."TrackId" = t."TrackId" JOIN "Invoice" inv ON il."InvoiceId" = inv."InvoiceId" JOIN "Customer" c ON inv."CustomerId" = c."CustomerId" LIMIT 10;'
```

Single-table SQL is in questions.txt under **warm-up only** — use for smoke tests, not main demos.

### 3. nosql2doc

```powershell
python -m agent.main --intent nosql2doc "Document this SQL: SELECT ar.\"Name\" AS artist, COUNT(al.\"AlbumId\") FROM \"Artist\" ar JOIN \"Album\" al ON ar.\"ArtistId\" = al.\"ArtistId\" GROUP BY ar.\"Name\""
```

### Bonus intents

```powershell
python -m agent.main --intent explain_sql --sql 'SELECT g."Name", COUNT(t."TrackId") FROM "Genre" g JOIN "Track" t ON g."GenreId" = t."GenreId" GROUP BY g."Name"'
python -m agent.main --intent validate_sql --sql 'SELECT c."FirstName", SUM(i."Total") FROM "Customer" c JOIN "Invoice" i ON c."CustomerId" = i."CustomerId" GROUP BY c."FirstName"'
python -m agent.main --json "Total invoice amount by customer country."
```

### Switch demo database

Both Chinook and Northwind can stay loaded in Docker:

```powershell
python -m agent.main --db-id northwind "Total revenue by category."
```

Or set `AGENT_DEMO_DB_ID=northwind` in `agent/.env`. Northwind multi-table questions: [data/standalone/northwind/questions.txt](data/standalone/northwind/questions.txt).

## Capstone demo set (multi-table)

Eight curated **join** questions for presentations — [data/standalone/chinook/questions.txt](data/standalone/chinook/questions.txt):

| ID | Question | Tables |
| --- | --- | --- |
| D1 | List album titles with artist names. | Artist + Album |
| D2 | List the top 5 tracks by unit price with album title and artist name. | Track + Album + Artist |
| D3 | Which artist has the most albums? | Artist + Album |
| D4 | Total invoice amount by customer country. | Customer + Invoice |
| D5 | Which customer has the highest total spending? | Customer + Invoice |
| D6 | How many tracks are in each genre? | Genre + Track |
| D7 | List all invoices from 2010 with customer first and last name. | Invoice + Customer |
| D8 | Show track name with genre name and media type name. | Track + Genre + MediaType |

Single-table warm-up questions are at the bottom of `questions.txt` — use only for quick sanity checks.

## Architecture

```text
User → Agent (LangGraph + Ollama orchestrator)
         ├─ Tool 1: Schema extractor
         ├─ Tool 2: CodeGen API (text2sql | sql2nosql | nosql2doc)
         └─ Tool 3: Postgres + Mongo execution
       → NL answer
```

Three **separate** task paths — orchestrator picks one intent per request (not a forced chain).

## MCP server

Exposes the same three tools over stdio MCP (default demo: **Chinook** from `agent/.env`):

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m agent.mcp.server
```

| MCP tool | Implementation |
| --- | --- |
| `extract_schema` | `tools/schema_tool.py` |
| `codegen_generate` | `tools/fastapi_tool.py` → CodeGen API |
| `execute_query` | `tools/execution_tool.py` |

Register in Cursor: copy [mcp/cursor-mcp.example.json](mcp/cursor-mcp.example.json) into Cursor MCP settings (adjust `cwd` / `PYTHONPATH` paths).

## Web UI (chat in browser)

Standalone FastAPI app under `agent/web/` — separate from `fastapi-deploy/` (CodeGen API).

```powershell
$env:PYTHONPATH = (Get-Location).Path
pip install -r agent\requirements.txt
python -m agent.web
```

Open **http://127.0.0.1:8080** — chat interface with example questions, intent selector, SQL panel, and result tables.

| Env var | Default | Purpose |
| --- | --- | --- |
| `AGENT_WEB_HOST` | `127.0.0.1` | Bind address |
| `AGENT_WEB_PORT` | `8080` | Port |
| `AGENT_WEB_RELOAD` | off | Auto-reload for development |

Same prerequisites as CLI: TEND Docker (Chinook), CodeGen API, Ollama (`gemma3:4b`).

## Capstone walkthrough (Stage 9)

One command for a live presentation — default set **D1, D3, D6** (reliable text2sql; avoid D2 three-table joins):

```powershell
$env:PYTHONPATH = (Get-Location).Path
python agent/scripts/run_capstone_demo.py
# or
python -m agent.main --demo
```

```powershell
python agent/scripts/run_capstone_demo.py --list          # all scenarios
python agent/scripts/run_capstone_demo.py --reliable-only
python agent/scripts/run_capstone_demo.py --ids D1,D3,S1
python agent/scripts/run_capstone_demo.py --pause 2       # pause between steps
```

Optional scenarios **D2, D4** (3-table / heavy aggregation) are marked *optional* — use if time allows.

### Orchestrator model (optional upgrade)

| Approach | Needed for capstone? | Notes |
| --- | --- | --- |
| **Embeddings / vector schema** | No | Keyword schema tool is enough for Chinook; future enhancement only |
| **Keep gemma3:4b + rules + honest summary** | Yes (current) | Fixes summary hallucination; intent uses rules first |
| **Qwen 2.5 7B via Ollama** | Optional | Slightly better prose; set `AGENT_ORCHESTRATOR_MODEL=qwen2.5:7b-instruct` — does **not** fix CodeGen SQL |
| **Retrain CodeGen** | Later | Fixes missing `COUNT(*)` in SELECT — not needed for demo with current honest answers |

SQL quality comes from **CodeGen LoRA**, not the orchestrator. Do not block the demo on embeddings or a new orchestrator.

## Tests

Unit + integration (skips if Postgres/Mongo offline):

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest agent/tests/ -q    # 88 tests
python agent/scripts/run_integration_tests.py
```

## Demo data

| DB | Postgres / Mongo | Questions + sample SQL |
| --- | --- | --- |
| **Chinook** (default) | `chinook` | [data/standalone/chinook/questions.txt](data/standalone/chinook/questions.txt) |
| **Northwind** | `northwind` | [data/standalone/northwind/questions.txt](data/standalone/northwind/questions.txt) |

Gold eval unchanged — uses TEND when `AGENT_DB_PROFILE=tend`. See [data/README.md](data/README.md).

## Spec

[doc/agent.md](doc/agent.md)
