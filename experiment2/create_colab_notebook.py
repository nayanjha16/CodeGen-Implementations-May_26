"""
Generates experiment2_colab.ipynb for running the CodeGen pipeline on Google Colab.

Usage (run once locally):
    python create_colab_notebook.py

Produces experiment2_colab.ipynb in the same directory.
Upload that file to Google Colab (File > Upload notebook).
"""

import json
import os


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


# ---------------------------------------------------------------------------
# Cell definitions
# ---------------------------------------------------------------------------

TITLE = md("""\
# CodeGen Pipeline — Google Colab
**Text-to-SQL / SQL-to-NoSQL / Text-to-NoSQL  |  Teacher-Student Distillation**

This notebook runs the full 7-stage pipeline with **Google Drive persistence**.
All trained models, predictions, logs, and generated data files are written to Drive
automatically after each stage so the run survives Colab disconnects.

> **Every session:** run all cells in **Section 1 (Setup)** top-to-bottom before
> resuming any stage.

| Stage | What it does | Estimated time (T4 GPU) |
|-------|--------------|-------------------------|
| 1 | Pass 1 fine-tuning | 3–4 hours |
| 2 | Pass 1 inference (×3 tasks) | 30–45 min |
| 3 | Extract Pass 1 failures | < 1 min |
| 4 | Teacher LLM annotation | 30–60 min |
| 5 | Pass 2 fine-tuning | 3–4 hours |
| 6 | Pass 2 inference (×3 tasks, no-RAG + RAG) | 2–3 hours |
| 7 | Compare Pass 1 vs Pass 2 | < 1 min |
""")

# ── S1: Mount Drive + configure paths + define helpers ──────────────────────

S1 = code("""\
# S1 — Mount Drive, configure paths, define helpers
# ============================================================
# Run this cell EVERY session before anything else.
# ============================================================
from google.colab import drive
drive.mount('/content/drive')

import os, sys, shutil, subprocess

# ── Paths ────────────────────────────────────────────────────
# Change DRIVE_BASE if you store the project in a different Drive folder.
DRIVE_BASE = '/content/drive/MyDrive/codegen/experiment2'
LOCAL_BASE  = '/content/experiment2'
DRIVE_ZIP   = '/content/drive/MyDrive/codegen/experiment2_colab.zip'

os.makedirs(LOCAL_BASE, exist_ok=True)
os.makedirs(DRIVE_BASE, exist_ok=True)

# ── Stage runner ─────────────────────────────────────────────
BAR = '=' * 64

def _run(label, *args):
    '''Run a pipeline script as a subprocess, streaming output line by line.'''
    import sys as _sys
    print(BAR)
    print('  ' + label)
    print(BAR, flush=True)
    env = {**os.environ, 'PYTHONUNBUFFERED': '1'}
    proc = subprocess.Popen(
        [_sys.executable] + list(args),
        cwd=LOCAL_BASE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        env=env,
    )
    for line in proc.stdout:
        print(line, end='', flush=True)
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(
            'Stage failed with exit code ' + str(proc.returncode)
        )
    print(BAR)
    print('  ' + label + ' — DONE')
    print(BAR, flush=True)

# ── Drive sync helpers ───────────────────────────────────────

def _copy(src, dst):
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)
    elif os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

def sync_to_drive(*items):
    '''Copy local items to Drive. Call after each stage.'''
    print('Syncing to Drive...')
    for d in items:
        src = os.path.join(LOCAL_BASE, d)
        dst = os.path.join(DRIVE_BASE, d)
        if os.path.exists(src):
            _copy(src, dst)
            print('  saved   ' + d)
        else:
            print('  skipped ' + d + '  (not found locally)')

def pull_from_drive(*items):
    '''Copy Drive items back to local. Call on session start.'''
    for d in items:
        src = os.path.join(DRIVE_BASE, d)
        dst = os.path.join(LOCAL_BASE, d)
        if os.path.exists(src):
            _copy(src, dst)
            print('  pulled  ' + d)
        else:
            print('  skipped ' + d + '  (not on Drive yet)')

print('Drive mounted.')
print('LOCAL_BASE : ' + LOCAL_BASE)
print('DRIVE_BASE : ' + DRIVE_BASE)
""")

# ── S2: First-time extraction OR reconnect pull ──────────────────────────────

S2 = code("""\
# S2 — Extract project zip OR pull saved state from Drive
# ============================================================
# Run this cell EVERY session.
# First time:  extracts zip and sets up the project directory.
# Reconnect:   re-extracts zip (source + data) and pulls back
#              any models/outputs/generated files from Drive.
# ============================================================
import zipfile

# Always (re-)extract the project zip so source files are fresh.
if os.path.exists(DRIVE_ZIP):
    print('Extracting ' + DRIVE_ZIP + ' ...')
    with zipfile.ZipFile(DRIVE_ZIP, 'r') as z:
        z.extractall('/content/')   # creates /content/experiment2/
    print('Extraction complete.')
else:
    print('WARNING: ' + DRIVE_ZIP + ' not found.')
    print('Ensure you uploaded experiment2_colab.zip to the Drive folder.')

# Pull previously saved checkpoints and outputs from Drive.
print()
print('Pulling saved artifacts from Drive...')
pull_from_drive('models', 'outputs', 'retrieval_index', 'logs')

# Pull generated data files individually (avoids syncing large SQLite databases).
for fpath in [
    'data/spider/text2sql_failures.json',
    'data/spider/spider_augmented_train.json',
    'docspider/docspider_ground_truth_dataset/sql2nosql_failures.json',
    'docspider/docspider_ground_truth_dataset/text2nosql_failures.json',
    'docspider/docspider_ground_truth_dataset/train_augmented.json',
]:
    pull_from_drive(fpath)

# Set working directory — all pipeline scripts use relative paths.
os.chdir(LOCAL_BASE)
print()
print('Working directory: ' + os.getcwd())
""")

# ── S3: Install dependencies ─────────────────────────────────────────────────

S3 = code("""\
# S3 — Install dependencies
# torch / numpy / scipy are pre-installed in Colab; excluded to avoid conflicts.
subprocess.run([
    sys.executable, '-m', 'pip', 'install', '-q',
    'peft==0.19.1',
    'transformers==5.9.0',
    'accelerate==1.13.0',
    'sentence-transformers==5.6.0',
    'rank-bm25==0.2.2',
    'sacrebleu==2.6.0',
    'bert-score==0.3.13',
    'nltk==3.9.4',
    'datasets==5.0.0',
    'tabulate==0.10.0',
    'openai',
    'anthropic',
], check=True)
print('Dependencies installed.')
""")

# ── S4: API keys ──────────────────────────────────────────────────────────────

S4 = code("""\
# S4 — Set API keys for Stage 4 (Teacher Annotation)
# Default provider is Groq (free, OpenAI-compatible).
# Get a free Groq key at console.groq.com — no credit card needed.
#
# Provider options (set whichever you use):
#   Groq      (free, recommended) — llama-3.3-70b-versatile
#   Together  (paid, best SQL)    — defog/sqlcoder-70b-alpha or Qwen2.5-Coder-72B
#   Fireworks (paid, best coder)  — Qwen/Qwen2.5-Coder-72B-Instruct
#   OpenAI                        — gpt-4o-mini
#   Anthropic                     — claude-haiku-4-5-20251001

os.environ['GROQ_API_KEY']      = ''   # gsk_...  (free at console.groq.com)
os.environ['TOGETHER_API_KEY']  = ''   # optional — for defog/sqlcoder or Qwen
os.environ['FIREWORKS_API_KEY'] = ''   # optional
os.environ['OPENAI_API_KEY']    = ''   # optional
os.environ['ANTHROPIC_API_KEY'] = ''   # optional

has_key = any(os.environ.get(k) for k in [
    'GROQ_API_KEY', 'TOGETHER_API_KEY', 'FIREWORKS_API_KEY',
    'OPENAI_API_KEY', 'ANTHROPIC_API_KEY',
])
print('API key configured.' if has_key else 'No API key set — Stage 4 must use mock teacher.')
""")

# ── S5: GPU check + pipeline status ──────────────────────────────────────────

S5 = code("""\
# S5 — Verify GPU and check which stages are already complete
import torch

print('PyTorch version : ' + torch.__version__)
print('CUDA available  : ' + str(torch.cuda.is_available()))
if torch.cuda.is_available():
    print('GPU device      : ' + torch.cuda.get_device_name(0))
    mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print('GPU memory      : ' + str(round(mem_gb, 1)) + ' GB')
else:
    print('WARNING: No GPU detected. Go to Runtime > Change runtime type > GPU.')

print()
print('--- Pipeline completion status ---')
STATUS = [
    ('Pass 1 model saved',      'models/codegen_pass1/adapter_model.safetensors'),
    ('Pass 1 text2sql done',    'outputs/codegen/pass1/text2sql/predictions.json'),
    ('Pass 1 sql2nosql done',   'outputs/codegen/pass1/sql2nosql/predictions.json'),
    ('Pass 1 text2nosql done',  'outputs/codegen/pass1/text2nosql/predictions.json'),
    ('Failures extracted',      'data/spider/text2sql_failures.json'),
    ('Teacher data ready',      'data/spider/spider_augmented_train.json'),
    ('Pass 2 model saved',      'models/codegen_pass2/adapter_model.safetensors'),
    ('Pass 2 text2sql done',    'outputs/codegen/pass2/text2sql/predictions.json'),
    ('Comparison report ready', 'outputs/comparison_report.txt'),
]
for label, path in STATUS:
    full = os.path.join(LOCAL_BASE, path)
    mark = 'done   ' if os.path.exists(full) else 'pending'
    print('  [' + mark + ']  ' + label)
""")

# ── Section headers ───────────────────────────────────────────────────────────

HDR_SANITY = md("""\
---
## Section 2: Sanity Test
Run this **once** before the full pipeline to verify your environment.
Uses 3 samples and a mock teacher — no API key needed, completes in ~5 minutes on GPU.
""")

HDR_PIPELINE = md("""\
---
## Section 3: Full Pipeline
Run stages **in order**. Sync cells save outputs to Drive immediately after each stage
so progress is safe if Colab disconnects. On reconnect, re-run Section 1 and skip
to the first incomplete stage.
""")

# ── Sanity test ───────────────────────────────────────────────────────────────

SANITY = code("""\
# Sanity test — 3 samples, mock teacher, no API key needed
# Verifies the full pipeline runs end-to-end before committing to a full run.
_run('Sanity test (3 samples, mock teacher)', 'run_codegen.py', '--sanity')
""")

# ── Stage 1 ───────────────────────────────────────────────────────────────────

STAGE1 = code("""\
# Stage 1 — Pass 1 Fine-tuning  (~3-4 hours on T4)
# Checkpoints written directly to Drive after every epoch.
# If this session disconnects mid-training, run the RESUME-STAGE1 cell
# in the next session (after running S1-S5 setup cells) to continue.
_run(
    'Stage 1 -- Pass 1 Fine-tuning',
    'finetune_unified.py',
    '--checkpoint_dir', DRIVE_BASE + '/models/codegen_pass1',
)
""")

RESUME1 = code("""\
# RESUME Stage 1 — ONLY run this if Stage 1 was interrupted mid-training.
# Continues from the latest epoch checkpoint already saved to Drive.
# Do NOT run on a fresh start — use STAGE1 instead.
_run(
    'Stage 1 -- Pass 1 Fine-tuning (RESUME)',
    'finetune_unified.py',
    '--checkpoint_dir', DRIVE_BASE + '/models/codegen_pass1',
    '--resume_training',
)
""")

SYNC1 = code("""\
# Sync Stage 1 logs to Drive (the model is already on Drive — checkpoint_dir pointed there)
sync_to_drive('logs')
""")

# ── Stage 2 ───────────────────────────────────────────────────────────────────

STAGE2 = code("""\
# Stage 2 — Pass 1 Inference  (~30-45 min on T4)
# Runs the Pass 1 model on the dev set for all 3 task types (no RAG).
# Writes: outputs/codegen/pass1/{text2sql,sql2nosql,text2nosql}/predictions.json

for task in ['text2sql', 'sql2nosql', 'text2nosql']:
    _run(
        'Stage 2 -- Pass 1 Inference: ' + task,
        'run_multi_task_inference.py',
        '--task', task,
        '--checkpoint_override', 'models/codegen_pass1',
        '--output_dir', 'outputs/codegen/pass1/' + task,
    )
""")

SYNC2 = code("""\
# Sync Stage 2 outputs to Drive
sync_to_drive('outputs/codegen/pass1', 'logs')
""")

# ── Stage 3 ───────────────────────────────────────────────────────────────────

STAGE3 = code("""\
# Stage 3 — Extract Pass 1 Failures  (< 1 min)
# Compares predictions against gold labels; writes failure records for the teacher.
# Writes: data/spider/text2sql_failures.json
#         docspider/.../sql2nosql_failures.json
#         docspider/.../text2nosql_failures.json

_run(
    'Stage 3 -- Extract Failures',
    'extract_failures.py',
    '--text2sql_pred',   'outputs/codegen/pass1/text2sql/predictions.json',
    '--sql2nosql_pred',  'outputs/codegen/pass1/sql2nosql/predictions.json',
    '--text2nosql_pred', 'outputs/codegen/pass1/text2nosql/predictions.json',
)
""")

SYNC3 = code("""\
# Sync Stage 3 outputs to Drive
sync_to_drive(
    'data/spider/text2sql_failures.json',
    'docspider/docspider_ground_truth_dataset/sql2nosql_failures.json',
    'docspider/docspider_ground_truth_dataset/text2nosql_failures.json',
    'logs',
)
""")

# ── Stage 4 ───────────────────────────────────────────────────────────────────

STAGE4 = code("""\
# Stage 4 — Teacher Annotation  (~30-60 min)
# Calls the teacher LLM to diagnose each failure and add a correction analysis.
# Default provider is Groq (free). Set GROQ_API_KEY in cell S4.
# Writes: data/spider/spider_augmented_train.json
#         docspider/.../train_augmented.json
#
# Choose ONE option below (comment/uncomment as needed):

# Option A — Groq llama-3.3-70b-versatile (default, free — set GROQ_API_KEY in S4):
_run('Stage 4 -- Teacher: Groq', 'generate_teacher_data.py')

# Option B — Together.ai defog/sqlcoder-70b (best for SQL, paid):
# _run('Stage 4 -- Teacher: Together/SQLCoder',
#      'generate_teacher_data.py',
#      '--provider', 'together',
#      '--model_id', 'defog/sqlcoder-70b-alpha')

# Option C — OpenAI gpt-4o-mini (paid):
# _run('Stage 4 -- Teacher: OpenAI', 'generate_teacher_data.py',
#      '--provider', 'openai', '--model_id', 'gpt-4o-mini')

# Option D — Mock teacher (no API key, synthetic annotations, for testing only):
# _run('Stage 4 -- Teacher: Mock', 'generate_teacher_data.py', '--mock_teacher')
""")

SYNC4 = code("""\
# Sync Stage 4 outputs to Drive
sync_to_drive(
    'data/spider/spider_augmented_train.json',
    'docspider/docspider_ground_truth_dataset/train_augmented.json',
    'logs',
)
""")

# ── Stage 5 ───────────────────────────────────────────────────────────────────

STAGE5 = code("""\
# Stage 5 — Pass 2 Fine-tuning  (~3-4 hours on T4)
# Checkpoints written directly to Drive after every epoch.
# Pass 1 weights are loaded from local (pulled from Drive in S2).
# If this session disconnects mid-training, run the RESUME-STAGE5 cell
# in the next session (after running S1-S5 setup cells) to continue.
_run(
    'Stage 5 -- Pass 2 Fine-tuning',
    'finetune_unified.py',
    '--spider_data',    'data/spider/spider_augmented_train.json',
    '--docspider_data', 'docspider/docspider_ground_truth_dataset/train_augmented.json',
    '--checkpoint_dir', DRIVE_BASE + '/models/codegen_pass2',
    '--resume_from',    'models/codegen_pass1',
)
""")

RESUME5 = code("""\
# RESUME Stage 5 — ONLY run this if Stage 5 was interrupted mid-training.
# Continues from the latest epoch checkpoint already saved to Drive.
# Do NOT run on a fresh start — use STAGE5 instead.
# Note: --resume_from is NOT needed here because the Pass 1 weights were
# already merged into the checkpoint saved on Drive.
_run(
    'Stage 5 -- Pass 2 Fine-tuning (RESUME)',
    'finetune_unified.py',
    '--spider_data',    'data/spider/spider_augmented_train.json',
    '--docspider_data', 'docspider/docspider_ground_truth_dataset/train_augmented.json',
    '--checkpoint_dir', DRIVE_BASE + '/models/codegen_pass2',
    '--resume_training',
)
""")

SYNC5 = code("""\
# Sync Stage 5 logs to Drive (the model is already on Drive — checkpoint_dir pointed there)
sync_to_drive('logs')
""")

# ── Stage 6 ───────────────────────────────────────────────────────────────────

STAGE6 = code("""\
# Stage 6 — Pass 2 Inference  (~2-3 hours on T4)
# 6 runs: 3 tasks x (no-RAG + RAG).
# RAG variant builds the retrieval index automatically if missing.
# Writes: outputs/codegen/pass2/{text2sql,sql2nosql,text2nosql}/predictions*.json

for task in ['text2sql', 'sql2nosql', 'text2nosql']:
    out = 'outputs/codegen/pass2/' + task

    # No-RAG
    _run(
        'Stage 6 -- Pass 2 no-RAG: ' + task,
        'run_multi_task_inference.py',
        '--task', task,
        '--checkpoint_override', 'models/codegen_pass2',
        '--output_dir', out,
    )

    # With RAG
    _run(
        'Stage 6 -- Pass 2 +RAG: ' + task,
        'run_multi_task_inference.py',
        '--task', task, '--rag',
        '--checkpoint_override', 'models/codegen_pass2',
        '--output_dir', out,
    )
""")

SYNC6 = code("""\
# Sync Stage 6 outputs to Drive
sync_to_drive('outputs/codegen/pass2', 'retrieval_index', 'logs')
""")

# ── Stage 7 ───────────────────────────────────────────────────────────────────

STAGE7 = code("""\
# Stage 7 — Compare Results  (< 1 min)
# Generates a side-by-side Pass 1 vs Pass 2 evaluation report.
# Writes: outputs/comparison_report.txt

_run('Stage 7 -- Compare Pass 1 vs Pass 2', 'compare_results.py')

# Final sync — saves everything to Drive
sync_to_drive(
    'outputs',
    'models',
    'retrieval_index',
    'logs',
    'data/spider/spider_augmented_train.json',
    'data/spider/text2sql_failures.json',
    'docspider/docspider_ground_truth_dataset/train_augmented.json',
    'docspider/docspider_ground_truth_dataset/sql2nosql_failures.json',
    'docspider/docspider_ground_truth_dataset/text2nosql_failures.json',
)
print()
print('Pipeline complete. All results saved to Drive.')
""")

# ── View results ──────────────────────────────────────────────────────────────

VIEW = code("""\
# View the comparison report
report = os.path.join(LOCAL_BASE, 'outputs', 'comparison_report.txt')
if os.path.exists(report):
    with open(report) as f:
        print(f.read())
else:
    print('comparison_report.txt not found. Run Stage 7 first.')
""")

# ---------------------------------------------------------------------------
# Assemble notebook
# ---------------------------------------------------------------------------

NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {
            "provenance": [],
            "gpuType": "T4",
            "toc_visible": True,
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
        },
        "accelerator": "GPU",
    },
    "cells": [
        TITLE,
        md("---\n## Section 1: Setup — Run Every Session\n"),
        S1,
        S2,
        S3,
        S4,
        S5,
        HDR_SANITY,
        SANITY,
        HDR_PIPELINE,
        md("### Stage 1 — Pass 1 Fine-tuning\n"),
        STAGE1,
        RESUME1,
        SYNC1,
        md("### Stage 2 — Pass 1 Inference\n"),
        STAGE2,
        SYNC2,
        md("### Stage 3 — Extract Failures\n"),
        STAGE3,
        SYNC3,
        md("### Stage 4 — Teacher Annotation\n"),
        STAGE4,
        SYNC4,
        md("### Stage 5 — Pass 2 Fine-tuning\n"),
        STAGE5,
        RESUME5,
        SYNC5,
        md("### Stage 6 — Pass 2 Inference\n"),
        STAGE6,
        SYNC6,
        md("### Stage 7 — Compare Results\n"),
        STAGE7,
        md("---\n## Section 4: View Results\n"),
        VIEW,
    ],
}

# ---------------------------------------------------------------------------
# Write notebook file
# ---------------------------------------------------------------------------

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment2_colab.ipynb")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(NOTEBOOK, f, indent=1, ensure_ascii=False)

print("Notebook written to: " + out_path)
print("Upload experiment2_colab.ipynb to Google Colab to run the pipeline.")
