# run_eval.py
import json
import subprocess
import sys  # <--- Make sure sys is imported!

# 1. Paths to your assets
GOLD_JSON_PATH = "data/spider/dev.json"
PRED_JSON_PATH = "outputs/zero_shot_predictions.json"

TMP_GOLD_TXT = "outputs/tmp_gold.txt"
TMP_PRED_TXT = "outputs/tmp_pred.txt"

print("🔄 Reformatting prediction and gold assets for the evaluation parser...")

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
        sql = item.get("predicted_sql", "SELECT *") or "SELECT *"
        f.write(f"{sql}\n")

print("✅ Alignment file formats staged successfully!")
print("📊 Launching Official Exact Match (EM) Evaluation Suite...\n")

# 4. Trigger evaluation.py using the exact same python executable as this environment
cmd = [
    sys.executable, "evaluation.py",  # <--- Changed "python" to sys.executable
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

# Simultaneously write it out to a permanent documentation file
REPORT_PATH = "outputs/evaluation_report.txt"
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(eval_run.stdout)

print(f"💾 Official baseline score report written to: {REPORT_PATH}")
