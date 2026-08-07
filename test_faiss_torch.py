import faiss
import torch
from transformers import AutoModelForCausalLM
print("Loading model...", flush=True)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-Coder-0.5B-Instruct", trust_remote_code=True)
print("Success", flush=True)
