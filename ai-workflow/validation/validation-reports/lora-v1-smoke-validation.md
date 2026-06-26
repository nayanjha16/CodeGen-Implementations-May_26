# LoRA v1 Smoke Validation Report

> **Date:** 2026-06-25  
> **Checkpoint run:** `v1` (50-sample smoke training)  
> **Eval samples:** 5 (Spider gold validation subset)

## Command

```bash
python scripts/validate_lora_smoke.py --version v1 --max-samples 5
```

Equivalent:

```bash
python scripts/run_baseline_eval.py \
  --adapter-run v1 \
  --max-samples 5 \
  --no-judge
```

## Adapter paths

| Task | Path |
|------|------|
| text2sql | `models/checkpoints/v1/text2sql/` |
| sql2nosql | `models/checkpoints/v1/sql2nosql/` |
| nosql2doc | `models/checkpoints/v1/nosql2doc/` |

## Results

Output: `results/spider_gold_validation_codegen-350M-multi_lora-v1_2506_2336/`

| Task | Syntax validity | Translation success | BLEU | ROUGE-L | BERTScore |
|------|-----------------|---------------------|------|---------|-----------|
| text2sql | 1.0000 | 1.0000 | 0.1958 | 0.7641 | 0.7764 |
| sql2nosql | 1.0000 | 1.0000 | 0.0496 | 0.5426 | 0.7958 |
| nosql2doc | 0.8000 | 0.8000 | 0.1361 | 0.3506 | 0.2888 |

## Passed checks

- All three v1 adapters load and generate without error
- Per-task adapter injection (text2sql / sql2nosql / nosql2doc models separate)
- Metrics JSON + detail CSVs written under `results/`
- Pipeline end-to-end on frozen gold validation subset

## Notes

- Smoke-trained adapters (50 rows); metrics are sanity checks only, not benchmark quality
- Ollama judge skipped (`--no-judge`); re-run with `--with-judge` when Ollama is available
- Full 50-sample eval: `python scripts/run_baseline_eval.py --adapter-run v1 --no-judge`
