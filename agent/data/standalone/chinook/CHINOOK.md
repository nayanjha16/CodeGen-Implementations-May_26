# Chinook demo (generated)

| Item | Value |
|------|-------|
| **Source** | [neondatabase/postgres-sample-dbs](https://github.com/neondatabase/postgres-sample-dbs) |
| **Upstream SQL** | `chinook_upstream.sql` |
| **Canonical dump** | `test.sql` (pg_dump from loaded DB) |
| **Postgres** | database `chinook`, schema `public`, **11 tables** |
| **Mongo** | database `chinook`, **11 collections**, 15607 documents |
| **Config** | `agent/.env` — default `AGENT_DEMO_DB_ID=chinook` |

## Sample tables

`Artist`, `Album`, `Track`, `Customer`, `Invoice`, `InvoiceLine`, `Employee`, `Genre`, …

(Mongo mirror uses lowercase collection names: `artist`, `album`, `track`, …)

## Sample agent questions

See **`questions.txt`** in this folder for the full demo list (text2sql, sql2nosql, doc).

Quick starters:

- How many customers are in the database?
- List the top 5 tracks by unit price
- Which artist has the most albums?
- Total invoice amount by country

## Switch from Northwind

Use `python -m agent.main --db-id chinook "..."` or set `AGENT_DEMO_DB_ID=chinook` in `agent/.env`. Both DBs can stay loaded in Docker.
