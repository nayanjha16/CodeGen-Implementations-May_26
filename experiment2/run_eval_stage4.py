# run_eval_stage4.py
import json
import subprocess
import sys
import os

# 1. Standardized with Linux forward slashes for Colab execution
GOLD_JSON_PATH = "data/spider/dev.json"
PRED_JSON_PATH = "outputs/stage4_schema_lora/stage4_schema_lora_predictions.json"

TMP_GOLD_TXT = "outputs/stage4_schema_lora/tmp_gold_stage4.txt"
TMP_PRED_TXT = "outputs/stage4_schema_lora/tmp_pred_stage4.txt"

# Ensure the output directory exists before writing files
os.makedirs("outputs/stage4_schema_lora", exist_ok=True)

print("🔄 Reformatting Stage 4 prediction and gold assets for the evaluation parser...")

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
    print("Please check that your Rank 8 run saved the file as 'stage4_schema_lora_predictions.json' inside that folder.")
    sys.exit(1)

with open(TMP_PRED_TXT, "w", encoding="utf-8") as f:
    for item in pred_data:
        sql = item.get("predicted_sql", "SELECT *") or "SELECT *"
        f.write(f"{sql}\n")

print("✅ Stage 4 alignment file formats staged successfully!")
print("📊 Launching Official Exact Match (EM) Evaluation Suite for Stage 4...\n")

# 4. Trigger evaluation.py 
cmd = [
    sys.executable, "evaluation.py",
    "--gold", TMP_GOLD_TXT,
    "--pred", TMP_PRED_TXT,
    "--db", "data/spider/database",
    "--table", "data/spider/tables.json",
    "--etype", "match"
]

# Run the evaluation script and capture its console outputs
eval_run = subprocess.run(cmd, capture_output=True, text=True)

# Print it live on your terminal so you can see it right now
print("=== EVALUATION ENGINE OUTPUT ===")
if eval_run.stdout:
    print(eval_run.stdout)
else:
    print("STDOUT is empty. Checking stderr for execution blockages:")
    print(eval_run.stderr)
print("=================================")

# Simultaneously write it out to a permanent documentation file
REPORT_PATH = "outputs/stage4_schema_lora/evaluation_report_stage4.txt"
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(eval_run.stdout)
    if eval_run.stderr:
        f.write("\n\n=== Errors/Warnings ===\n")
        f.write(eval_run.stderr)

print(f"💾 Official Stage 4 score report written to: {REPORT_PATH}")