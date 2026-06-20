# run_stage4_experiment_try1.py
import os
import json
import torch
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Pulling configuration paths directly from your project config
from src.config import STAGE4_CHECKPOINT_PATH, DATASET_PATH, TABLES_PATH
from src.loader import load_spider_tasks

def construct_stage4_prompt(task, schema_map):
    db_id = task.get("db_id", "")
    question = task.get("question", "")
    ddl_schema = schema_map.get(db_id, "-- Schema information unavailable\n")
    
    # 💡 Upgraded instruction block with explicit anti-hallucination constraints
    prompt = (
        f"### Instruction:\n"
        f"Convert the natural language question to a valid SQL query for the database: {db_id}.\n"
        f"STRICT EXECUTION RULES:\n"
        f"1. ONLY select columns explicitly listed in the CREATE TABLE blocks below.\n"
        f"2. Do NOT invent aggregate attributes (e.g., do NOT use 'Highest', 'Lowest', 'Highest_Attendance').\n"
        f"3. Do NOT perform a JOIN if the question can be resolved using a single table.\n\n"
        f"### Schema:\n"
        f"{ddl_schema}\n"
        f"### Question:\n"
        f"{question}\n\n"
        f"### Response:\n"
        f"SELECT"
    )
    return prompt

def inline_load_schema_mappings(tables_json_path):
    """
    Builds clean, standard SQL DDL style representations for each database.
    This structures attributes into typed blocks that smaller models can follow.
    """
    schema_map = {}
    with open(tables_json_path, "r", encoding="utf-8") as f:
        tables_data = json.load(f)
        
    for db in tables_data:
        db_id = db["db_id"]
        table_names = db["table_names_original"]
        column_names = db["column_names_original"]
        column_types = db["column_types"]
        
        # Group column definitions by table index
        table_columns = {i: [] for i in range(len(table_names))}
        for idx, (table_idx, col_name) in enumerate(column_names):
            if table_idx != -1:  # Skip wildcard *
                col_type = column_types[idx]
                table_columns[table_idx].append(f"    {col_name} {col_type}")
        
        # Construct classic pseudo-DDL syntax blocks
        ddl_tables = []
        for idx, t_name in enumerate(table_names):
            cols_str = ",\n".join(table_columns[idx])
            ddl_table = f"CREATE TABLE {t_name} (\n{cols_str}\n);"
            ddl_tables.append(ddl_table)
            
        schema_map[db_id] = "\n\n".join(ddl_tables)
    return schema_map

def main():
    print("📥 [STAGE 4] Initializing Full-Scale Schema-Informed LoRA Pipeline...")
    
    # 1. Load Data (Keep at 50 for local evaluation loop baseline stability)
    all_tasks = load_spider_tasks(DATASET_PATH, limit=50) 
    schema_map = inline_load_schema_mappings(TABLES_PATH)
    
    # 2. Initialize Base Model and Tokenizer
    base_model_name = "Salesforce/codegen-350M-mono" 
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 3. Load Your Local Fine-Tuned Weights
    print(f"🔩 Attaching weights from: {STAGE4_CHECKPOINT_PATH}")
    model = PeftModel.from_pretrained(base_model, STAGE4_CHECKPOINT_PATH)
    model.eval()
    
    predictions = []
    print(f"🚀 Processing all {len(all_tasks)} tasks with optimized constraints & beam decoding...")
    
    # 4. Optimized Generation Loop
    for idx, task in enumerate(all_tasks):
        prompt = construct_stage4_prompt(task, schema_map)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                # 💡 Swapped greedy decoding for Beam Search to look ahead and avoid structural loops
                num_beams=4,
                early_stopping=True
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predicted_sql = "SELECT *"
        
        if "### Response:" in generated_text:
            response_block = generated_text.split("### Response:")[-1].strip()
            
            # Force-restore anchor prefix safely if truncated by the split
            if not response_block.upper().startswith("SELECT"):
                response_block = "SELECT " + response_block
            
            # 💡 Robust Extraction: Isolate string before any trailing template blocks
            raw_query = response_block.split("###")[0].strip()
            
            # 💡 Multi-line flattening: Merge structure safely to avoid newline fragmentation
            predicted_sql = " ".join(raw_query.splitlines())
            predicted_sql = " ".join(predicted_sql.split())
            
            # 💡 Standardize literals: Convert double quotes to single quotes for exact match compatibility
            predicted_sql = predicted_sql.replace('"', "'")
            
        predictions.append({
            "db_id": task["db_id"],
            "question": task["question"],
            "gold_query": task["query"],
            "predicted_sql": predicted_sql
        })
        
        if (idx + 1) % 10 == 0:
            print(f"   Processed {idx + 1}/{len(all_tasks)} tasks...")

    # =====================================================================
    # 5. Save Optimized Try1 Results Safely
    # =====================================================================
    target_dir = os.path.join("outputs", "stage4_schema_lora_r16_try1")
    os.makedirs(target_dir, exist_ok=True)
    
    master_output_path = os.path.join(target_dir, "stage4_schema_lora_predictions.json")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    historical_output_path = os.path.join(target_dir, f"stage4_schema_lora_predictions_{timestamp}.json")
    
    # Clean file-write execution with perfect indentation mapping
    for path in [master_output_path, historical_output_path]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, indent=4)
        
    print(f"✅ Stage 4 execution complete!")
    print(f"💾 Active evaluation target: {master_output_path}")
    print(f"💾 Non-destructive timeline archive: {historical_output_path}")

if __name__ == "__main__":
    main()