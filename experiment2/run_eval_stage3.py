# run_eval_stage3.py
import json
import subprocess
import sys

# 1. Paths to your assets (Updated for Stage 3)
GOLD_JSON_PATH = "data/spider/dev.json"
PRED_JSON_PATH = "outputs/stage3_lora/stage3_lora_predictions.json"  # <-- Inputting Stage 3 JSON

TMP_GOLD_TXT = "outputs/tmp_gold_stage3.txt"              # <-- Unique temp file
TMP_PRED_TXT = "outputs/tmp_pred_stage3.txt"              # <-- Unique temp file

print("🔄 Reformatting Stage 3 prediction and gold assets for the evaluation parser...")

# 2. Extract and format the Gold Queries
with open(GOLD_JSON_PATH, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

with open(TMP_GOLD_TXT, "w", encoding="utf-8") as f:
    for item in gold_data:
        f.write(f"{item['query']}\t{item['db_id']}\n")

# 3. Extract and format your Model's Predicted Queries
with open(PRED_JSON_PATH, "r", encoding="utf-8") as f:
    pred_data = json.load(f)

with open(TMP_PRED_TXT, "w", encoding="utf-8") as f:
    for item in pred_data:
        # Pull the predicted SQL string from the Stage 3 structure
        sql = item.get("predicted_sql", "SELECT *") or "SELECT *"
        f.write(f"{sql}\n")

print("✅ Stage 3 alignment file formats staged successfully!")
print("📊 Launching Official Exact Match (EM) Evaluation Suite for Stage 3...\n")

# 4. Trigger evaluation.py using the exact same python executable as this environment
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
print(eval_run.stdout)

# Simultaneously write it out to a permanent documentation file (Updated for Stage 3)
REPORT_PATH = "outputs/evaluation_report_stage3.txt"
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(eval_run.stdout)

print(f"💾 Official Stage 3 score report written to: {REPORT_PATH}")