import torch
from transformers import AutoModelForCausalLM
print("Loading model on mps...")
model = AutoModelForCausalLM.from_pretrained("Saikrishna2511/qwen-multitask", trust_remote_code=True)
model.to("mps")
print("Success")
