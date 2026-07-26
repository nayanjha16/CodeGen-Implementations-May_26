# Testing Strategy — Full Spec

> Covers all `agent.md` §5 capabilities, not a single-path MVP.

## Layers

| Layer | Tool | Validates |
| --- | --- | --- |
| Adapter eval | `scripts/run_baseline_eval.py` | LoRA quality on gold 50 |
| Agent E2E | `agent/tests/` + manual CLI | Tools + orchestrator + HTTP |

## Capability test cases

### Text → SQL

- db_ids: `concert_singer`, `pets_1`
- New NL questions (not in gold JSONL)
- Retry: inject wrong table once → recovery within 3 attempts

### SQL → MongoDB

- Provide gold SQL from JSONL
- CodeGen returns Mongo query
- Execute on TEND Mongo

### SQL documentation

- Provide Mongo query
- CodeGen returns documentation text
- Optional: compare to gold `documentation` field (embedding or judge)

### Explain SQL

- Provide SQL string
- Ollama returns step-by-step explanation
- Must not emit a different executable query as primary output

### Query validation

- Safe SELECT → pass
- DROP / DELETE → blocked
- Unknown table → fail before execute

## MCP tests

- Each tool callable via MCP server
- Same result as direct Python call

## Integration prerequisites

Same as gold eval — see [../../docs/gold-set-commands.md](../../docs/gold-set-commands.md):

- TEND Docker up
- Cloud Run `/health` loaded
- Ollama orchestrator model pulled

## Pass criteria for capstone demo

- [ ] All three MCP tools registered and documented
- [ ] Text2SQL E2E with execution
- [ ] SQL2NoSQL E2E with Mongo execution
- [ ] Documentation generation without execute
- [ ] Explain SQL via Ollama
- [ ] Validation blocks unsafe SQL
- [ ] Retry loop demonstrated on forced error
- [ ] Agent never returns SQL without going through CodeGen tool (log audit)
