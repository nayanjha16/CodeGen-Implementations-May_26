# -*- coding: utf-8 -*-
"""
CodeGen Experiment 2 - Module 2: Grounded SQL to NoSQL Fine-Tuning
Target Architecture: Causal Decoder (Salesforce/codegen-350M-mono)
"""

import json
import os
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model, TaskType

# Import your helper functions from our updated loader script
from src.loader import load_schema_context_map

# ==========================================
# 1. INITIALIZE ENVIRONMENT & TOKENIZER
# ==========================================
MODEL_ID = "Salesforce/codegen-350M-mono"
DOCSPIDER_TRAIN_PATH = "docspider/docspider_ground_truth_dataset/train.json"
DOCSPIDER_COLLECTIONS_PATH = "docspider/docspider_ground_truth_dataset/collections.json"

print("📥 Initializing Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

# ==========================================
# 2. LOAD AND PARSE SCHEMA MAP AND DATASET
# ==========================================
print("📂 Parsing Database Schema Metadata Matrix...")
schema_context_map = load_schema_context_map(DOCSPIDER_COLLECTIONS_PATH)

print(f"📊 Loading training dataset from: {DOCSPIDER_TRAIN_PATH}")
with open(DOCSPIDER_TRAIN_PATH, "r", encoding="utf-8") as f:
    docspider_train = json.load(f)

flattened_data = []
for entry in docspider_train:
    db_id = entry.get("db_id", "").strip()
    sql_query = entry.get("spider_gold_sql", "").strip()
    mql_query = entry.get("query", "").strip()
    
    if sql_query and mql_query and db_id:
        flattened_data.append({
            "db_id": db_id,
            "sql": sql_query,
            "mql": mql_query
        })

def tokenize_function(examples):
    batch_input_ids = []
    batch_labels = []
    
    for db_id, sql, target in zip(examples['db_id'], examples['sql'], examples['mql']):
        schema_info = schema_context_map.get(db_id, "Unknown schema footprint")
        
        # 📝 Grounded Prompt Construction
        prompt_part = (
            f"### Instruction:\n"
            f"Using the database schema provided, translate the SQL query into an executable MongoDB NoSQL query.\n"
            f"### Schema:\n{schema_info}\n"
            f"### SQL:\n{sql}\n"
            f"### Response:\n"
        )
        target_part = f"{target}<|endoftext|>"
        
        prompt_ids = tokenizer.encode(prompt_part, add_special_tokens=False)
        target_ids = tokenizer.encode(target_part, add_special_tokens=False)
        
        input_ids = prompt_ids + target_ids
        
        # 🎯 CRITICAL: Mask out the prompt tokens with -100 so loss is calculated ONLY on target NoSQL
        labels = [-100] * len(prompt_ids) + target_ids
        
        if len(input_ids) > 512:
            input_ids = input_ids[:512]
            labels = labels[:512]
            
        batch_input_ids.append(input_ids)
        batch_labels.append(labels)
        
    return {"input_ids": batch_input_ids, "labels": batch_labels}

print("⚙️ Compiling training data into token matrices...")
raw_dataset = Dataset.from_list(flattened_data)
tokenized_dataset = raw_dataset.map(tokenize_function, batched=True, remove_columns=raw_dataset.column_names)

print(f"✅ Total records compiled for fine-tuning: {len(tokenized_dataset)}")

# ==========================================
# 3. INITIALIZE MODEL FROM CLEAN BASE WEIGHTS
# ==========================================
print("⚙️ Loading clean foundational base weights...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["qkv_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, peft_config)
print("✅ Isolated LoRA Layer Matrix Active!")
model.print_trainable_parameters()

# ==========================================
# 4. CONFIGURING EXECUTION TRAINER ENGINE
# ==========================================
print("🏋️‍♂️ Setting up training configurations...")
training_args = TrainingArguments(
    output_dir="./models/stage5_model_weights_checkpoint-1265",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    num_train_epochs=5,
    save_strategy="epoch",
    eval_strategy="no",
    fp16=True,
    warmup_ratio=0.03,
    weight_decay=0.01,
    report_to="none"
)

data_collator = DataCollatorForSeq2Seq(
    tokenizer,
    pad_to_multiple_of=8,
    return_tensors="pt",
    padding=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator
)

print("🚀 Starting fine-tuning loop! Tracking loss optimization...")
trainer.train()

trainer.save_model("./models/stage5_model_weights_checkpoint-1265")
print("✅ Grounded fine-tuning run finalized and saved successfully!")