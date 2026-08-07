# Execution Guide

All commands are run from the `experiment2/` directory.

---

## Local CPU

### 1. Prerequisites

- Python 3.9+
- ~8 GB free disk (models + indexes)
- ~4 GB RAM minimum (8 GB recommended)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Fine-tune both models on both tasks

```bash
python run_all.py --skip_eval
```

Fine-tuning skips automatically if a checkpoint already exists (`adapter_config.json` present).  
To fine-tune one model or one task only:

```bash
python run_all.py --skip_eval --model_type codegen
python run_all.py --skip_eval --model_type codet5
python run_all.py --skip_eval --task text2sql
```

### 4. Baseline inference + evaluation

```bash
python run_all.py --skip_train
```

Outputs saved to:
```
outputs/codegen/text2sql/evaluation_report.txt
outputs/codegen/sql2nosql/evaluation_report.txt
outputs/codet5/text2sql/evaluation_report.txt
outputs/codet5/sql2nosql/evaluation_report.txt
```

### 5. Build RAG retrieval index  *(one-time, from training data only)*

```bash
pip install sentence-transformers>=2.7.0 rank-bm25>=0.2.2
python scripts/build_retrieval_index.py
```

Outputs:
```
retrieval_index/text2sql_embeddings.npy    (~10 MB)
retrieval_index/text2sql_metadata.json
retrieval_index/sql2nosql_embeddings.npy   (~6 MB)
retrieval_index/sql2nosql_metadata.json
```

### 6. RAG inference + evaluation

```bash
python run_all.py --skip_train --rag
```

Outputs saved to:
```
outputs/codegen/text2sql/evaluation_report_rag.txt
outputs/codegen/sql2nosql/evaluation_report_rag.txt
outputs/codet5/text2sql/evaluation_report_rag.txt
outputs/codet5/sql2nosql/evaluation_report_rag.txt
```

### 7. Final comparison table (8 rows)

```bash
python compare_results.py
```

Prints and saves to `outputs/comparison_report.txt`.

---

### Quick reference

| Goal | Command |
|---|---|
| Full run (no RAG) | `python run_all.py` |
| Fine-tune only | `python run_all.py --skip_eval` |
| Inference only (baseline) | `python run_all.py --skip_train` |
| Inference only (RAG) | `python run_all.py --skip_train --rag` |
| One model, one task | `python run_all.py --model_type codet5 --task text2sql` |
| Comparison table | `python compare_results.py` |
| Build index only | `python scripts/build_retrieval_index.py` |

---

## Google Colab (T4 GPU)

### 1. Upload files

Upload the entire `experiment2/` folder to Google Drive.  
Suggested path: `My Drive/codegen/experiment2/`

### 2. Open the notebook

Open `colab_runner.ipynb` in Colab.  
*(File → Open notebook → Google Drive → navigate to experiment2/)*

### 3. Set runtime

Runtime → Change runtime type → **T4 GPU**

### 4. Run cells in order

| Cell | What it does |
|---|---|
| **Verify GPU** | `nvidia-smi` — confirms T4 is allocated |
| **Mount Drive** | Mounts Drive and `cd` into `experiment2/` |
| **Install deps** | `pip install -r requirements.txt` |
| **Install RAG deps** | `pip install sentence-transformers rank-bm25` |
| **Run option** | Choose one run cell (A–E) — see below |
| **RAG: build index** | `python scripts/build_retrieval_index.py` |
| **RAG: run inference** | `python run_all.py --skip_train --rag` |
| **Show results** | `python compare_results.py` |
| **Download outputs** | Downloads `outputs/` as a zip |

### 5. Run options (choose one)

| Option | Cell | Command |
|---|---|---|
| A | Both models, both tasks | `python run_all.py` |
| B | CodeGen only | `python run_all.py --model_type codegen` |
| C | CodeT5+ only | `python run_all.py --model_type codet5` |
| D | NL→SQL only | `python run_all.py --task text2sql` |
| E | Skip fine-tuning | `python run_all.py --skip_train` |

### 6. Recommended Colab sequence (full experiment)

```
Cell: Verify GPU
Cell: Mount Drive
Cell: Install deps
Cell: Install RAG deps
Cell: Option A  (fine-tune + baseline inference, ~2–4 hrs on T4)
Cell: RAG: build index  (~2 min on T4)
Cell: RAG: run inference  (~30–60 min on T4)
Cell: Show results
Cell: Download outputs
```

### Notes

- The notebook is a **launcher only** — all logic is in the `.py` scripts.
- Fine-tuning is skipped automatically if checkpoints already exist; safe to re-run.
- The retrieval index only needs to be built once; it reads from `retrieval_index/` on subsequent runs.
- If the Colab session disconnects, restart and run from **Option E** (skip fine-tuning) to resume inference from existing checkpoints.
