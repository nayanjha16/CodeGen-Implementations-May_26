# run_isolated_nosql_experiment.py
import os
import json
from datetime import datetime
from peft import PeftModel
from tqdm import tqdm

# Import modular configuration and infrastructure
from src.config import (
    DOCSPIDER_DEV_PATH,
    EXP2_NOSQL_CHECKPOINT_PATH
)
from src.loader import load_spider_tasks, construct_nosql_prompt
from src.generator import initialize_model_and_tokenizer, generate_nosql_prediction
from src.processor import clean_generated_nosql

# Hardcode the direct output path to Google Drive to protect against runtime wipes
ISOLATED_OUTPUT_PATH = "/content/drive/MyDrive/codegen_lora_sql_to_nosql/results/isolated_nosql_predictions.json"

def main():
    print("🧪 [STAGE 5 - ISOLATED] Launching SQL-to-NoSQL Isolated Evaluation Loop...")
    
    # 1. Load evaluation dataset from DocSpider config path
    eval_tasks = load_spider_tasks(DOCSPIDER_DEV_PATH, limit=None)
    
    # 2. Initialize foundational base model weights ONCE
    base_model, tokenizer = initialize_model_and_tokenizer(stage='exp2')
    
    # 3. Load the NoSQL adapter weights ONCE into VRAM before entering the loop
    print("🔩 Loading Module 2 (SQL-to-NoSQL) into VRAM...")
    nosql_model = PeftModel.from_pretrained(base_model, EXP2_NOSQL_CHECKPOINT_PATH)
    nosql_model.eval()
    
    # Ensure output folders exist safely on Google Drive
    os.makedirs(os.path.dirname(ISOLATED_OUTPUT_PATH), exist_ok=True)
    
    # Advanced inference parameters to combat hallucinations & infinite loops
    gen_kwargs = {
        "max_new_tokens": 128,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "num_beams": 1,
        "temperature": 0.0,
        "do_sample": False,
        "repetition_penalty": 1.2,          # 🛑 Antidote to token looping
        "no_repeat_ngram_size": 4           # 🛑 Breaks syntax echoing
    }
    
    isolated_results = []
    print(f"🚀 Feeding {len(eval_tasks)} Flawless GOLD SQL Queries directly to Adapter...")
    print(f"💾 Active trace tracking directed to: {ISOLATED_OUTPUT_PATH}\n")
    
    # 4. Processing Loop (Now incredibly optimized)
    for idx, task in enumerate(tqdm(eval_tasks)):
        # Bypassing Module 1 completely to check raw conversion accuracy
        gold_sql = task.get("spider_gold_sql", "")
        
        # Format the isolated prompt using the true ground-truth SQL
        nosql_prompt = construct_nosql_prompt(gold_sql)
        
        # Generate prediction using the generation parameters
        raw_nosql_output = generate_nosql_prediction(nosql_model, tokenizer, nosql_prompt, **gen_kwargs)
        predicted_mql = clean_generated_nosql(raw_nosql_output)
        
        # Compile Performance Records
        isolated_results.append({
            "db_id": task.get("db_id", ""),
            "question": task.get("question", ""),
            "input_gold_sql": gold_sql,
            "gold_mql": task.get("query", ""),
            "predicted_mql": predicted_mql
        })
        
        # Real-time disk persistence to Google Drive every 10 steps
        if (idx + 1) % 10 == 0 or (idx + 1) == len(eval_tasks):
            with open(ISOLATED_OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(isolated_results, f, indent=4)
                
    # 5. Create Chronological Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_path = ISOLATED_OUTPUT_PATH.replace(".json", f"_{timestamp}.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(isolated_results, f, indent=4)
        
    print("\n" + "="*80)
    print(f"✅ Isolated SQL-to-NoSQL Evaluation Finalized Fast!")
    print(f"💾 Master Results: {ISOLATED_OUTPUT_PATH}")
    print(f"💾 Timeline Archive: {backup_path}")
    print("="*80)

if __name__ == "__main__":
    main()