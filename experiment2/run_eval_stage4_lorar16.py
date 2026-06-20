# run_eval_stage4_r16.py
import json
import subprocess
import sys
import os

# 1. Paths dynamically joined to handle Windows environments natively
GOLD_JSON_PATH = os.path.join("data", "spider", "dev.json")
PRED_JSON_PATH = os.path.join("outputs", "stage4_schema_lora_r16", "stage4_schema_lora_predictions.json")

# Isolating our temporary text targets to the new R16 folder
R16_DIR = os.path.join("outputs", "stage4_schema_lora_r16")
os.makedirs(R16_DIR, exist_ok=True)

TMP_GOLD_TXT = os.path.join(R16_DIR, "tmp_gold_r16.txt")
TMP_PRED_TXT = os.path.join(R16_DIR, "tmp_pred_r16.txt")
REPORT_PATH = os.path.join(R16_DIR, "evaluation_report_r16.txt")

print("🔄 Reformatting Rank 16 prediction and gold assets for the evaluation parser...")

# 2. Extract and format the Gold Queries
with open(GOLD_JSON_PATH, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

with open(TMP_GOLD_TXT, "w", encoding="utf-8") as f:
    for item in gold_data:
        f.write(f"{item['query']}\t{item['db_id']}\n")

# 3. Extract and format your Model's Predicted Queries
try:
    with open(PRED_JSON_PATH, "r", encoding="utf-8") as f:
        pred_data = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: Could not find prediction file at: {PRED_JSON_PATH}")
    sys.exit(1)

with open(TMP_PRED_TXT, "w", encoding="utf-8") as f:
    for item in pred_data:
        sql = item.get("predicted_sql", "SELECT *") or "SELECT *"
        f.write(f"{sql}\n")

print("✅ Rank 16 alignment file formats staged successfully!")
print("📊 Launching Official Exact Match (EM) Evaluation Suite for Rank 16...\n")

# 4. Trigger evaluation.py with explicit cross-platform path mapping
cmd = [
    sys.executable, "evaluation.py",
    "--gold", TMP_GOLD_TXT,
    "--pred", TMP_PRED_TXT,
    "--db", os.path.join("data", "spider", "database"),
    "--table", os.path.join("data", "spider", "tables.json"),
    "--etype", "match"
]

# Run the evaluation script and capture its console outputs
eval_run = subprocess.run(cmd, capture_output=True, text=True)

# Print it live to your PowerShell console
print("=== EVALUATION ENGINE OUTPUT ===")
if eval_run.stdout:
    print(eval_run.stdout)
else:
    print("STDOUT is empty. Checking stderr for execution errors:")
    print(eval_run.stderr)
print("=================================")

# Simultaneously write it out to a permanent documentation file
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(eval_run.stdout)
    if eval_run.stderr:
        f.write("\n\n=== Errors/Warnings ===\n")
        f.write(eval_run.stderr)

print(f"💾 Official Rank 16 score report written to: {REPORT_PATH}")