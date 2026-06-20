# run_stage4_experiment.py
import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Pulling configuration paths directly from your project config
from src.config import STAGE4_CHECKPOINT_PATH, DATASET_PATH, TABLES_PATH, STAGE4_OUTPUT_PATH
from src.loader import load_spider_tasks

def construct_stage4_prompt(task, schema_map):
    """
    Stage 4 Prompt: Clean, unified schema grounding format.
    Keeps prompt complexity minimal to prevent attention fragmentation.
    """
    db_id = task.get("db_id", "")
    question = task.get("question", "")
    ddl_schema = schema_map.get(db_id, "-- Schema information unavailable\n")
    
    prompt = (
        f"### Instruction:\n"
        f"Using the database schema provided below, convert this question to SQL for database: {db_id}\n\n"
        f"### Schema:\n"
        f"{ddl_schema}\n\n"
        f"### Question:\n"
        f"{question}\n\n"
        f"### Response:\n"
    )
    return prompt

def inline_load_schema_mappings(tables_json_path):
    """
    Directly reads your local tables.json to extract structural schema mappings
    without relying on external loader dependencies.
    """
    schema_map = {}
    with open(tables_json_path, "r", encoding="utf-8") as f:
        tables_data = json.load(f)
        
    for db in tables_data:
        db_id = db["db_id"]
        schema_text = ""
        table_names = db["table_names_original"]
        column_names = db["column_names_original"]
        
        for t_idx, table_name in enumerate(table_names):
            columns = [col[1] for col in column_names if col[0] == t_idx]
            schema_text += f"Table {table_name}, Columns: [{', '.join(columns)}]\n"
            
        schema_map[db_id] = schema_text
    return schema_map

def main():
    print("📥 [STAGE 4] Initializing Full-Scale Schema-Informed LoRA Pipeline...")
    
    # 1. Load Data (Set limit=None to process all 1,034 validation tasks)
    all_tasks = load_spider_tasks(DATASET_PATH, limit=None) 
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
    print(f"🚀 Processing all {len(all_tasks)} tasks locally with schema context...")
    
    # 4. Local Generation Loop
    for idx, task in enumerate(all_tasks):
        prompt = construct_stage4_prompt(task, schema_map)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id,
                num_beams=1,          # Deterministic decoding
                temperature=0.0       # Stable greedy decoding
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predicted_sql = "SELECT *"
        if "### Response:" in generated_text:
            predicted_sql = generated_text.split("### Response:")[-1].strip().split("\n")[0].strip()
            
        predictions.append({
            "db_id": task["db_id"],
            "question": task["question"],
            "gold_query": task["query"],
            "predicted_sql": predicted_sql
        })
        
        if (idx + 1) % 50 == 0:
            print(f"   Processed {idx + 1}/{len(all_tasks)} tasks...")

    # 5. Save Stage 4 Results Locally
    output_path = STAGE4_OUTPUT_PATH

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)
        
    print(f"✅ Stage 4 local execution complete! Output saved to {output_path}")

if __name__ == "__main__":
    main()