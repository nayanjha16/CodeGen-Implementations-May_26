# Running the CodeGen Pipeline on Google Colab

---

## Prerequisites

- A Google account with Google Drive (~5 GB free space needed)
- A Colab account (free tier works; Pro recommended for longer runtimes)
- A free Groq API key for Stage 4 — get one at **console.groq.com** (no credit card needed)
  - Alternatively: Together.ai, Fireworks.ai, OpenAI, or Anthropic key; or use the mock teacher for testing

---

## Step 1 — Prepare the zip file

Create `experiment2_colab.zip` containing the project source and data files.
**Do not include** `venv/`, `logs/`, `models/`, `outputs/`, `retrieval_index/`,
`legacy/`, `data/spider/database/`, or `data/spider/test_database/`.

Run this from the `experiment2/` directory on your PC:

```bash
python -c "
import zipfile, os

INCLUDE_DIRS  = ['src', 'scripts', 'docspider/docspider_ground_truth_dataset']
INCLUDE_FILES = [
    'run_codegen.py', 'finetune_unified.py', 'run_multi_task_inference.py',
    'extract_failures.py', 'generate_teacher_data.py', 'compare_results.py',
    'evaluation.py', 'process_sql.py', 'stage5_evaluate_by_execution.py',
    'requirements_colab.txt',
    'data/spider/train_spider.json',
    'data/spider/dev.json',
    'data/spider/tables.json',
]

with zipfile.ZipFile('experiment2_colab.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in INCLUDE_FILES:
        z.write(f, os.path.join('experiment2', f))
    for d in INCLUDE_DIRS:
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in ('__pycache__', '.git')]
            for fn in files:
                path = os.path.join(root, fn)
                z.write(path, os.path.join('experiment2', path))

print('Created experiment2_colab.zip')
"
```

Expected size: ~60–80 MB (dominated by `train_spider.json` at ~14 MB).

---

## Step 2 — Generate the Colab notebook

Run the generator script to produce the `.ipynb` file:

```bash
python create_colab_notebook.py
```

This writes `experiment2_colab.ipynb` in the same directory.

---

## Step 3 — Upload to Google Drive

Upload both files to your Drive under `My Drive/codegen/`:

```
My Drive/
└── codegen/
    ├── experiment2_colab.zip      ← project source + data
    └── experiment2_colab.ipynb    ← open this in Colab
```

The notebook's `DRIVE_BASE` variable defaults to `My Drive/codegen/experiment2/`.
If you put the zip elsewhere, update `DRIVE_BASE` and `DRIVE_ZIP` in cell S1.

---

## Step 4 — Open the notebook in Colab

1. In Google Drive, right-click `experiment2_colab.ipynb` → **Open with Google Colaboratory**
2. Go to **Runtime > Change runtime type** → set **Hardware accelerator** to **T4 GPU** → Save

---

## Step 5 — Run the Setup section (every session)

Run cells S1 through S5 in order at the start of every Colab session:

| Cell | What it does |
|------|--------------|
| S1   | Mounts Drive, sets paths, defines `_run()`, `sync_to_drive()`, `pull_from_drive()` |
| S2   | Extracts the project zip; pulls saved models/outputs from Drive |
| S3   | Installs Python dependencies (skips torch/numpy already in Colab) |
| S4   | Sets your API key (Groq recommended — free, no credit card) |
| S5   | Checks GPU availability and shows which stages are already complete |

---

## Step 6 — Run the sanity test first

Before committing to the full pipeline (~10 hours), run the sanity test cell.
It runs all 7 stages on 3 samples with a mock teacher in ~5 minutes:

```python
_run('Sanity test', 'run_codegen.py', '--sanity')
```

If this completes without errors, your environment is ready.

---

## Step 7 — Run the full pipeline, stage by stage

Run each stage cell followed immediately by its sync cell.
**Do not skip the sync cell** — it saves the stage's output to Drive.

### Expected runtimes on T4 GPU (16 GB)

| Stage | Cell | Runtime |
|-------|------|---------|
| 1 — Pass 1 fine-tuning | STAGE1 + SYNC1 | 3–4 hours |
| 2 — Pass 1 inference | STAGE2 + SYNC2 | 30–45 min |
| 3 — Extract failures | STAGE3 + SYNC3 | < 1 min |
| 4 — Teacher annotation | STAGE4 + SYNC4 | 30–60 min |
| 5 — Pass 2 fine-tuning | STAGE5 + SYNC5 | 3–4 hours |
| 6 — Pass 2 inference | STAGE6 + SYNC6 | 2–3 hours |
| 7 — Compare + final sync | STAGE7 | < 1 min |

Total: ~10–13 hours. Free-tier Colab (12 h max session) may require 2 sessions.
Colab Pro (24 h sessions, A100 GPU option) can complete it in one session.

### Stage 4 — Teacher provider options

The default provider is **Groq** (free, no credit card).
Set `GROQ_API_KEY` in cell S4, then run the STAGE4 cell.

To switch providers, edit `src/config.py` before running Stage 4:

| Provider | Free? | Best for | `provider` | `base_url` | `model_id` |
|----------|-------|----------|-----------|-----------|------------|
| **Groq** (default) | Yes | general | `"groq"` | `"https://api.groq.com/openai/v1"` | `"llama-3.3-70b-versatile"` |
| Together.ai | Paid | text2sql | `"together"` | `"https://api.together.xyz/v1"` | `"defog/sqlcoder-70b-alpha"` |
| Together.ai | Paid | coder | `"together"` | `"https://api.together.xyz/v1"` | `"Qwen/Qwen2.5-Coder-72B-Instruct"` |
| OpenAI | Paid | general | `"openai"` | `None` | `"gpt-4o-mini"` |
| Anthropic | Paid | general | `"anthropic"` | n/a | `"claude-haiku-4-5-20251001"` |
| Mock | Free | testing | n/a | n/a | run with `--mock_teacher` |

To use the mock teacher (no API key):
```python
_run('Stage 4', 'generate_teacher_data.py', '--mock_teacher')
```

---

## Resuming after a disconnect

1. Open the notebook in Colab again
2. **Runtime > Change runtime type** — re-select GPU
3. Run cells **S1 through S5** (Setup section)
4. Cell S5 prints the completion status — look for the first `[pending]` entry
5. Jump to that stage cell and continue

Because every sync cell writes output to Drive, and S2 pulls Drive → local at
session start, you resume exactly where you left off.

### Example: session ended after Stage 2

```
  [done   ]  Pass 1 model saved
  [done   ]  Pass 1 text2sql done
  [done   ]  Pass 1 sql2nosql done
  [done   ]  Pass 1 text2nosql done
  [pending]  Failures extracted        ← start here
  [pending]  Teacher data ready
  ...
```

Run cells: S1 → S2 → S3 → S4 → S5 → **STAGE3 → SYNC3 → STAGE4 → ...**

---

## Drive folder layout after a full run

```
My Drive/codegen/experiment2/
├── models/
│   ├── codegen_pass1/          ← Pass 1 LoRA adapter (~21 MB)
│   └── codegen_pass2/          ← Pass 2 LoRA adapter (~21 MB)
├── outputs/
│   └── codegen/
│       ├── pass1/{text2sql,sql2nosql,text2nosql}/predictions.json
│       └── pass2/{text2sql,sql2nosql,text2nosql}/predictions*.json
│       comparison_report.txt
├── retrieval_index/            ← BM25 + dense embeddings (~50 MB)
├── logs/                       ← one log file per subprocess
├── data/spider/
│   ├── text2sql_failures.json
│   └── spider_augmented_train.json
└── docspider/docspider_ground_truth_dataset/
    ├── sql2nosql_failures.json
    ├── text2nosql_failures.json
    └── train_augmented.json
```

---

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `DRIVE_ZIP not found` | Zip not uploaded to the right Drive path | Upload to `My Drive/codegen/experiment2_colab.zip` or update `DRIVE_ZIP` in S1 |
| `ModuleNotFoundError: src` | Working directory not set | Re-run cell S2; it sets `os.chdir(LOCAL_BASE)` |
| `CUDA out of memory` | Batch size too large for GPU | Reduce `train_batch` in `src/config.py` from 4 to 2 before zipping |
| `No module named openai` | S3 not run this session | Run cell S3 |
| `API key not set` | Stage 4 with no key | Either set key in S4 or use Option C (mock teacher) in STAGE4 |
| `adapter_model.safetensors not found` in Stage 5 | Stage 1 not complete or not synced | Check Drive for `models/codegen_pass1/`; re-run SYNC1 |
| HuggingFace download stalls | Hub connectivity | Runtime > Restart and re-run; Hub download retries automatically |
