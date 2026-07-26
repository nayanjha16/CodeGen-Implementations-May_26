# Gold Set (50 samples) — Command List

Simplified copy-paste commands for **Spider gold validation** eval → compare → publish → deploy.

Dataset: `data/spider_gold_validation.jsonl` (50 examples)  
Paths below use your Windows setup — adjust if your folders differ.

---

## 1. Start databases (TEND Docker)

```powershell
cd C:\Users\Bhavani\Documents\Codegen\TEND
docker compose up -d postgres mongo
```

**First time only** (or after `docker compose down -v`) — import gold subset tables:

```bash
# Git Bash or WSL, from TEND repo root
./scripts/import_jsonl_tables.sh
```

**Quick check** (optional):

```powershell
docker exec tend-postgres-1 psql -U tend -d tend_spider -tAc "SELECT COUNT(*) FROM concert_singer.singer;"
docker exec tend-mongo-1 mongosh --quiet --eval "db.getSiblingDB('spider_concert_singer').singer.countDocuments()"
```

Expect `6` for both.

---

## 2. Ollama judge (documentation metrics)

```powershell
ollama serve
```

```powershell
ollama pull gemma3:4b
ollama list
```

---

## 3. Session setup (every new terminal)

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
```

Required in `.env`:

```text
TEND_REPO_PATH=C:/Users/Bhavani/Documents/Codegen/TEND
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_JUDGE_MODEL=gemma3:4b
OLLAMA_TIMEOUT=120
```

---

## 4. Baseline eval (no adapter, n=50)

```powershell
python scripts/run_baseline_eval.py --max-samples 50 --output spider_gold_validation_codegen-350M-multi_baseline-v3
```

Confirm at startup:

```text
Baseline Evaluation: Salesforce/codegen-350M-multi
Documentation judge (ollama): gemma3:4b
Database execution available: True
```

Output:

```text
results/spider_gold_validation_codegen-350M-multi_baseline-v3/metrics.json
```

---

## 5. LoRA eval (after adapters exist under models/checkpoints/v3/)

```powershell
python scripts/run_baseline_eval.py --adapter-run v3 --max-samples 50 --output spider_gold_validation_codegen-350M-multi_lora-v3
```

Output:

```text
results/spider_gold_validation_codegen-350M-multi_lora-v3/metrics.json
```

Compare both `metrics.json` files before publishing.

---

## 6. Publish adapters to Hugging Face Hub

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
$env:PYTHONPATH = "fastapi-deploy"
```

Dry-run:

```powershell
python fastapi-deploy/publish/push_adapters.py --version v3 --dry-run
```

Publish:

```powershell
hf auth login
python fastapi-deploy/publish/push_adapters.py --version v3
```

---

## 7. Update manifest

Edit `fastapi-deploy/manifest.yaml`:

```yaml
checkpoint_version: v3
```

---

## 8. Deploy Cloud Run

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
python fastapi-deploy/infra/cloudrun/deploy.py
```

---

## 9. Verify deployment

Wait for cold start (~1–3 min), then:

```powershell
curl.exe -s "https://codegen-api-161349047936.asia-south2.run.app/health"
```

Expect `"checkpoint_version": "v3"` and `"loaded": true`.

Sample call:

```powershell
curl.exe -X POST "https://codegen-api-161349047936.asia-south2.run.app/v1/chat/completions" `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"codegen-text2sql\",\"intent\":\"text2sql\",\"messages\":[{\"role\":\"user\",\"content\":\"Schema:\nCREATE TABLE singer (singer_id REAL PRIMARY KEY, name TEXT);\n\nQuestion: How many singers do we have?\"}]}'
```

---

## Version tags (replace `v3` as needed)

| Step | Example output name |
| --- | --- |
| Baseline v1 | `..._baseline-v1` |
| LoRA v1 | `..._lora-v1` |
| Baseline v3 | `..._baseline-v3` |
| LoRA v3 | `..._lora-v3` |
| Baseline v4 | `..._baseline-v4` |
| LoRA v4 | `..._lora-v4` |

Same commands — only change `--output`, `--adapter-run`, `--version`, and `checkpoint_version`.

---

## Optional flags

```powershell
# Skip Ollama judge (faster)
python scripts/run_baseline_eval.py --max-samples 50 --no-judge --output ...

# Smoke test (5 samples)
python scripts/run_baseline_eval.py --max-samples 5 --output ..._smoke
```
