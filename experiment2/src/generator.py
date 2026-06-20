# src/generator.py
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel  # Added for Stage 3 weight integration
# Import both standard and Stage 3 configuration targets
from src.config import (
    MODEL_ID, 
    STAGE3_MODEL_ID, 
    STAGE3_CHECKPOINT_PATH, 
    DEVICE, 
    MAX_NEW_TOKENS, 
    TEMPERATURE
)

def initialize_model_and_tokenizer(stage=1):
    """
    Loads the CodeGen model and tokenizer into memory based on config settings.
    stage=1 or 2: Loads baseline multi-lingual model.
    stage=3: Loads mono model wrapped with custom fine-tuned LoRA weights.
    Ensures correct left-padding configuration for decoder-only generation.
    """
    # Select target model ID based on the requested experiment stage
    if stage == 3:
        target_model_id = STAGE3_MODEL_ID
        print(f"📥 [STAGE 3] Loading Fine-Tuned LoRA configurations from: '{STAGE3_CHECKPOINT_PATH}'...")
    else:
        target_model_id = MODEL_ID
        print(f"📥 [STAGE {stage}] Loading tokenizers and weights for '{target_model_id}'...")
        
    start_load = time.time()
    
    tokenizer = AutoTokenizer.from_pretrained(target_model_id)
    
    # CRITICAL: Causal models must pad on the left for proper batch completion
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    # 1. Load the underlying base model architecture
    # (Using float16 here matching our training state to conserve memory)
    base_model = AutoModelForCausalLM.from_pretrained(
        target_model_id,
        torch_dtype=torch.float16 if stage == 3 else None
    )
    
    # 2. If Stage 3, wrap the base model with the local adapter checkpoints
    if stage == 3:
        model = PeftModel.from_pretrained(base_model, STAGE3_CHECKPOINT_PATH)
    else:
        model = base_model
        
    model.to(DEVICE)
    model.eval()
    
    print(f"🎯 Model loaded successfully onto: [{DEVICE.upper()}] ({time.time() - start_load:.2f}s)")
    return model, tokenizer

def generate_sql_prediction(model, tokenizer, prompt_text):
    """
    Executes a pure greedy inference pass on the input prompt.
    Splices out the prompt text to return ONLY the newly generated tokens.
    """
    inputs = tokenizer(
        prompt_text, 
        return_tensors="pt", 
        padding=True, 
        return_attention_mask=True
    ).to(DEVICE)
    
    # --- CRITICAL: DEFINE STOPPING TOKENS HERE ---
    # 204 is newline (\n), 26 is semicolon (;) in CodeGen tokenizers
    stop_token_ids = [tokenizer.eos_token_id, 26, 204]

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=MAX_NEW_TOKENS,         
            do_sample=False,         
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=stop_token_ids  
        )
        
    # Extract only the newly generated tokens (slice past input length)
    input_len = inputs.input_ids.shape[1]
    generated_tokens = outputs[0][input_len:]
    
    return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()