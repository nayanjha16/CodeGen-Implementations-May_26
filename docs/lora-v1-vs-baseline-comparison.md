# LoRA v1 vs Baseline — Spider Gold Validation

> **Project:** CodeGen Fine-Tuning with PEFT & LoRA  
> **Date:** 2026-06-25  
> **Model:** `Salesforce/codegen-350M-multi`  
> **LoRA adapter:** `v1`  
> **Judge model:** `qwen3:4b`  
> **Dataset:** `spider_gold_validation` (50 examples per task)

## Training context

LoRA v1 was fine-tuned on **50 training samples** for **10 epochs** (smoke-scale run). Evaluation below uses the full 50-example Spider gold validation split.

## Compared runs

| Run | Path |
|-----|------|
| Baseline (no adapter) | `results/spider_gold_validation_codegen-350M-multi_2506_2029/metrics.json` |
| LoRA v1 | `results/spider_gold_validation_codegen-350M-multi_lora-v1_2506_2343/metrics.json` |

## Summary

LoRA v1 improves every task on similarity and validity metrics. The clearest win is **text2sql judge accuracy** (4% → 14%). **sql2nosql** and **documentation** show large gains in output quality and parseability, but judge scores stay flat at 8% and 0% respectively.

---

## Text2SQL — strongest judge improvement

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 4% | **14%** | **+10 pp (+250%)** |
| CodeBLEU / BERTScore | 0.548 | 0.629 | +0.081 (+15%) |
| ROUGE-L | 0.415 | 0.580 | +0.165 (+40%) |
| BLEU | 0.044 | 0.113 | +0.069 (+157%) |
| Syntax validity | 98% | **100%** | +2 pp |
| Translation success | 92% | **100%** | +8 pp |

Exact match and execution accuracy remain 0% for both runs.

---

## SQL2NoSQL — large metric gains, judge unchanged

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 8% | 8% | 0 |
| CodeBLEU | 0.202 | 0.514 | +0.312 (+154%) |
| Token F1 | 0.241 | 0.547 | +0.306 (+127%) |
| Structural equivalence | 44% | **76%** | +32 pp |
| Syntax validity | 26% | **98%** | +72 pp |
| Translation success | 26% | **98%** | +72 pp |
| Exact match | 4% | 0% | −4 pp |

---

## Documentation — big quality jump, judge still 0%

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 0% | 0% | 0 |
| CodeBLEU | 0.030 | 0.244 | +0.214 (+705%) |
| Token F1 | 0.049 | 0.336 | +0.287 (+587%) |
| ROUGE-L | 0.051 | 0.306 | +0.255 (+496%) |
| Structural equivalence | 12% | **40%** | +28 pp |
| Syntax validity | 28% | **76%** | +48 pp |
| Translation success | 28% | **76%** | +48 pp |

---

## Takeaways

- **Text2SQL:** LoRA v1 is the clearest win — **3.5×** judge accuracy (4% → 14%) plus better semantic overlap and full syntax/translation success.
- **SQL2NoSQL & documentation:** Much better generated outputs (validity, structure, similarity), but the LLM judge does not reflect that yet for documentation (0%) and is flat for sql2nosql (8%).
- **Still weak:** Execution accuracy is 0% everywhere; exact match is still 0% for text2sql and documentation.
- **Training scale:** Despite training on only 50 samples for 10 epochs, LoRA v1 already shows meaningful gains over the unfine-tuned baseline — especially on text2sql.
