# src/generator.py
import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from src.config import MODELS, get_device_settings
import time
from src.logger import pipeline_logger

# ---------------------------------------------------------------------------
# Dynamic Configuration Binding
# ---------------------------------------------------------------------------
# Resolve the execution device string directly from your config function
DEVICE = get_device_settings()["device"]

# Pull model specifications with clean fallbacks from the config dictionary
MODEL_ID = MODELS["codegen"].get("model_id", "Salesforce/codegen-350M-multi")
MAX_NEW_TOKENS = MODELS["codegen"].get("max_target_len", 150)
NUM_BEAMS      = MODELS["codegen"].get("num_beams", 4)

# Synchronize the checkpoint tracking directory path
UNIFIED_CHECKPOINT_PATH = MODELS["codegen"].get("checkpoint_dir", "models/codegen_multitask")

# Legacy variables preserved for backward compatibility with isolated pipelines
STAGE3_MODEL_ID = MODEL_ID
STAGE3_CHECKPOINT_PATH = "models/codegen_stage3"
EXP2_NOSQL_CHECKPOINT_PATH = "models/codegen_nosql"


# ---------------------------------------------------------------------------
# Model Loader Engine
# ---------------------------------------------------------------------------
def initialize_model_and_tokenizer(stage=1, adapter_path=None):
    """
    Loads the model and tokenizer into execution memory.
    
    stage=1 or 2: Loads baseline models.
    stage=3     : Loads legacy mono model wrapped with Stage 3 LoRA weights.
    stage='exp2': Loads foundational mono model for legacy dual-stage pipelines.
    stage='unified': Loads the multi-task model with calibration hooks.
    """
    if stage == 'unified':
        target_model_id = MODEL_ID  
        checkpoint_target = adapter_path if adapter_path else UNIFIED_CHECKPOINT_PATH
        print(f"📥 [UNIFIED MULTI-TASK] Loading Multi-Task Adapter weights from: '{checkpoint_target}'...")
    elif stage == 3:
        target_model_id = STAGE3_MODEL_ID
        checkpoint_target = STAGE3_CHECKPOINT_PATH
        print(f"📥 [STAGE 3] Loading Fine-Tuned LoRA configurations from: '{checkpoint_target}'...")
    elif stage == 'exp2':
        target_model_id = MODEL_ID
        checkpoint_target = EXP2_NOSQL_CHECKPOINT_PATH
        print(f"📥 [EXPERIMENT 2] Initializing base weights for Dual-Stage Pipeline...")
    else:
        target_model_id = MODEL_ID
        checkpoint_target = None
        print(f"📥 [STAGE {stage}] Loading tokenizers and weights for '{target_model_id}'...")
        
    start_load = time.time()
    
    tokenizer = AutoTokenizer.from_pretrained(target_model_id)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    base_model = AutoModelForCausalLM.from_pretrained(
        target_model_id,
        torch_dtype=get_device_settings()["codegen_dtype"]
    )
    
    # Conditionally attach structural adapter weights with explicit path validation
    if checkpoint_target and os.path.exists(checkpoint_target):
        print(f"   ↳ Found weights at target directory. Injecting PEFT adapter layer...")
        model = PeftModel.from_pretrained(base_model, checkpoint_target)
    else:
        if checkpoint_target:
            print(f"   ⚠️ Warning: Checkpoint path '{checkpoint_target}' not found. Defaulting to zero-shot base parameters.")
        model = base_model
        
    model.to(DEVICE)
    model.eval()
    
    print(f"🎯 Model loaded successfully onto: [{str(DEVICE).upper()}] ({time.time() - start_load:.2f}s)")
    return model, tokenizer


# ---------------------------------------------------------------------------
# Prediction Execution Interfaces
# ---------------------------------------------------------------------------

def generate_sql_prediction(model, tokenizer, prompt_text, is_unified=True):
    """
    Executes a greedy inference pass on the input prompt for SQL.
    Splices out the prompt text to return ONLY the newly generated tokens.
    """
    start_time = time.perf_counter()
    
    # 1. Tokenize inputs
    inputs = tokenizer(
        prompt_text, 
        return_tensors="pt", 
        padding=True, 
        return_attention_mask=True
    ).to(DEVICE)
    
    # 2. Determine stop tokens
    if is_unified:
        stop_token_ids = [tokenizer.eos_token_id]
    else:
        stop_token_ids = [tokenizer.eos_token_id, 26, 204]

    # 3. Model generation
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=NUM_BEAMS,
            do_sample=False,
            early_stopping=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=stop_token_ids,
        )

    # 4. Decode output
    input_len = inputs.input_ids.shape[1]
    generated_tokens = outputs[0][input_len:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    # 5. Log the execution stats
    latency = time.perf_counter() - start_time
    pipeline_logger.record(
        stage="inference",
        action="generate_sql",
        input_data=prompt_text,
        output_data=generated_text,
        stats={
            "latency_sec": round(latency, 4),
            "input_tokens": input_len,
            "output_tokens": len(generated_tokens)
        }
    )
    
    return generated_text

def generate_nosql_prediction(model, tokenizer, prompt_text):
    """
    Executes an inference pass tailored for MongoDB syntax generation.
    Bypasses structural line-breaking tokens to ensure complete nested document structures.
    """
    start_time = time.perf_counter()
    
    # 1. Tokenize inputs
    inputs = tokenizer(
        prompt_text, 
        return_tensors="pt", 
        padding=True, 
        return_attention_mask=True
    ).to(DEVICE)

    # 2. Model generation
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=NUM_BEAMS,
            do_sample=False,
            early_stopping=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
        
    # 3. Decode output
    input_len = inputs.input_ids.shape[1]
    generated_tokens = outputs[0][input_len:]
    generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
    
    # 4. Log the execution stats
    latency = time.perf_counter() - start_time
    pipeline_logger.record(
        stage="inference",
        action="generate_nosql",
        input_data=prompt_text,
        output_data=generated_text,
        stats={
            "latency_sec": round(latency, 4),
            "input_tokens": input_len,
            "output_tokens": len(generated_tokens)
        }
    )
    
    return generated_text