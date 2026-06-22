# evaluate_by_execution.py
import json
import re

def find_all_keywords_in_mongo_result(mongodb_result_str):
    JSON_PUNC_START_CHARS = ['[','{']
    JSON_PUNC_END_CHARS = [']','}']
    JSON_PUNC_CHARS = [' ', ','] + JSON_PUNC_START_CHARS + JSON_PUNC_END_CHARS
    keywords = set()
    i, j = 0, 0
    while i < len(mongodb_result_str) and j < len(mongodb_result_str):
        while j < len(mongodb_result_str) and mongodb_result_str[j] != ':':
            j += 1
        if j < len(mongodb_result_str) - 1 and mongodb_result_str[j-1] != '"':
            i = j
            abort = False
            while i > 0 and (mongodb_result_str[i] not in JSON_PUNC_CHARS):
                if mongodb_result_str[i] == '\'':
                    abort = True
                    break
                i -= 1
            if not abort:
                i += 1
                keywords.add(mongodb_result_str[i:j])
        i = j
        j += 1
    return list(keywords)

def translate_mongo_result(mongodb_result_str):
    """ Official DocSpider normalization logic to clear out structural syntax flavor """
    if not mongodb_result_str or mongodb_result_str.strip() == "":
        return []
        
    result_str = mongodb_result_str.replace('}{', '},{')
    result_str = result_str.replace(r'_id:\s*null', '_id: "null"')
    # To this (Note the 'r' prefix):
    result_str = re.sub(r'\s*_?id:\s*ObjectId\(\'[a-z0-9]+\'\),?', "", result_str)
    result_str = re.sub(r'_id:\s*{[^}]+}', "", result_str)
    
    if "Long('" in result_str:
        while True:
            try:
                long_index = result_str.index("Long('")
                start_index = long_index + len("Long('")
                end_index = start_index
                while result_str[end_index] != "'":
                    end_index += 1
                result_str = result_str[0: long_index] + result_str[start_index:end_index] + result_str[end_index+2:]
            except ValueError:
                break

    if ":" in result_str:
        keywords = find_all_keywords_in_mongo_result(result_str)
        keywords = sorted(keywords, key=len, reverse=True)
        for keyword in keywords:
            result_str = result_str.replace(f"{keyword}:" , '"' + keyword + '":')
        if not result_str.startswith("[") and not result_str.endswith("]"):
            result_str = "[" + result_str + "]"
        try:
            mongodb_original_result_object = eval(result_str)
        except:
            mongodb_original_result_object = []
        
        result_object = []
        for original_result_row in mongodb_original_result_object:
            try:
                result_object.append(tuple(original_result_row.values()))
            except:
                result_object.append((original_result_row,))
    else:
        result_str = ",".join("\"" + x + "\"" for x in result_str.split("\n") if x.strip() != "")
        if not result_str.startswith("[") and not result_str.endswith("]"):
            result_str = "[" + result_str + "]"
        try:
            mongodb_original_result_object = eval(result_str)
            result_object = [(row,) for row in mongodb_original_result_object]
        except:
            result_object = []
            
    return result_object

import json
import os
import re

# ... Keep your find_all_keywords_in_mongo_result and translate_mongo_result functions here ...

def evaluate_pipeline(pipeline_json_path):
    # 🌟 CROSS-REFERENCE MAP: Point this exactly to your local dev.json file
    DEV_JSON_PATH = "./docspider/docspider_ground_truth_dataset/dev.json"  # Adjust this path if your dev.json is in a different folder
    
    difficulty_lookup = {}
    if os.path.exists(DEV_JSON_PATH):
        print(f"📖 Building difficulty reference map from: {DEV_JSON_PATH}")
        with open(DEV_JSON_PATH, "r", encoding="utf-8") as f:
            dev_data = json.load(f)
            for item in dev_data:
                # Use the clean question text as a unique key
                difficulty_lookup[item["question"].strip()] = item.get("difficulty", "medium").lower()
    else:
        print(f"⚠️ Warning: Could not find raw dev.json at {DEV_JSON_PATH}. Breakdown will default to medium.")

    print(f"📥 Loading generated experimental predictions from: {pipeline_json_path}")
    with open(pipeline_json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    metrics = {cat: {"correct": 0, "total": 0} for cat in ["easy", "medium", "hard", "extra"]}
    total_correct = 0
    
    for idx, item in enumerate(records):
        question_text = item.get("question", "").strip()
        
        # Pull difficulty from our lookup dictionary, fallback to medium if missing
        category = difficulty_lookup.get(question_text, "medium")
        if "extra" in category:
            category = "extra"
            
        gold_mql = item.get("gold_mql", "").strip()
        pred_mql = item.get("predicted_mql", "").strip()
        
        gold_obj = translate_mongo_result(gold_mql)
        pred_obj = translate_mongo_result(pred_mql)
        
        if gold_obj == [] and pred_obj == [] and gold_mql != pred_mql:
            is_match = False
        else:
            is_match = (len(gold_obj) == len(pred_obj) and set(gold_obj) == set(pred_obj))
            
        metrics[category]["total"] += 1
        if is_match:
            metrics[category]["correct"] += 1
            total_correct += 1
            
    print("\n📊 OFFICIAL DOCSPIDER EXECUTION RESULTS SCORECARD")
    print("=" * 55)
    for cat in ["easy", "medium", "hard", "extra"]:
        data = metrics[cat]
        acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
        print(f"🔹 {cat.upper():<7} Accuracy : {data['correct']}/{data['total']} ({acc:.2f}%)")
    
    overall_acc = (total_correct / len(records) * 100) if records else 0
    print("=" * 55)
    print(f"📈 TOTAL DATA EXECUTION ACCURACY: {overall_acc:.2f}%")
    print("=" * 55)
    
# --- Generate Report Text ---
    report_lines = []
    report_lines.append("=======================================================")
    report_lines.append("📊 OFFICIAL DOCSPIDER EXECUTION RESULTS REPORT")
    report_lines.append("=======================================================")
    report_lines.append(f"📅 Evaluation Run Date : 2026-06-22")
    report_lines.append(f"📥 Predictions Source  : {pipeline_json_path}")
    report_lines.append(f"📖 Reference Source    : {DEV_JSON_PATH}")
    report_lines.append("-------------------------------------------------------")
    
    for cat in ["easy", "medium", "hard", "extra"]:
        data = metrics[cat]
        acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
        report_lines.append(f"🔹 {cat.upper():<7} Accuracy : {data['correct']}/{data['total']} ({acc:.2f}%)")
    
    overall_acc = (total_correct / len(records) * 100) if records else 0
    report_lines.append("=======================================================")
    report_lines.append(f"📈 TOTAL DATA EXECUTION ACCURACY: {overall_acc:.2f}%")
    report_lines.append("=======================================================")
    
    # 1. Print to console for immediate visibility
    report_text = "\n".join(report_lines)
    print("\n" + report_text)
    
    # 2. Save securely to a local file
    output_dir = "outputs/evaluation_reports"
    os.makedirs(output_dir, exist_ok=True)
    report_file_path = os.path.join(output_dir, "stage5_baseline_execution_report.txt")
    
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"💾 Evaluation report successfully archived to: {report_file_path}")

if __name__ == "__main__":
    PIPELINE_PREDS = "outputs/experiment2_pipeline_results/pipeline_predictions.json"
    evaluate_pipeline(PIPELINE_PREDS)