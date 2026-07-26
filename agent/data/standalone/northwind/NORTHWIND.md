# Northwind demo (generated)

| Item | Value |
|------|-------|
| **Source** | [pthom/northwind_psql](https://github.com/pthom/northwind_psql) |
| **Upstream SQL** | `northwind_upstream.sql` (downloaded as-is) |
| **Canonical dump** | `test.sql` (pg_dump from loaded DB) |
| **Postgres** | database `northwind`, schema `public`, **14 tables** |
| **Mongo** | database `northwind`, **14 collections**, 3362 documents |
| **Config** | `agent/.env` — set `AGENT_DEMO_DB_ID=northwind` or use `--db-id northwind` |

## Sample tables

`categories`, `customers`, `employees`, `orders`, `order_details`, `products`, `suppliers`, `shippers`, …

## Sample agent questions

See **`questions.txt`** in this folder for the full demo list (text2sql, sql2nosql, doc).

Quick starters:

- How many customers are there?
- List top 5 products by unit price
- Which employee handled the most orders?
- Total revenue by category

## Regenerate `test.sql` from Postgres

```powershell
docker exec tend-postgres-1 pg_dump -U tend -d northwind --schema=public --no-owner --no-privileges --format=plain `
  > agent/data/standalone/northwind/test.sql
```

## Reload from scratch

```powershell
$env:AGENT_DEMO_POSTGRES_DATABASE = "northwind"
$env:AGENT_DEMO_MONGO_DATABASE = "northwind"
$env:AGENT_DEMO_SQL_DUMP = "agent\data\standalone\northwind\test.sql"
.\agent\scripts\setup_demo_postgres.ps1 -UseTend -Force
python agent\scripts\mirror_postgres_to_mongo.py --skip-postgres --force
```
