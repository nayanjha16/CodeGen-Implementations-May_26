"""Real codegen-350M baseline on HumanEval via execution accuracy (pass@1/pass@5).
Run in Colab with a GPU after: pip install transformers torch datasets.
"""
import sys, json, os, importlib.util
import numpy as np
from collections import Counter
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from datasets import load_dataset

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("execmod", os.path.join(HERE, "src/sandbox/execution.py"))
execution = importlib.util.module_from_spec(spec); sys.modules["execmod"] = execution
spec.loader.exec_module(execution)
check_correctness = execution.check_correctness

STOPS = ["\ndef ", "\nclass ", "\nif __name__", "\nprint(", "\n@"]
def truncate(t):
    cut = len(t)
    for s in STOPS:
        i = t.find(s)
        if i != -1: cut = min(cut, i)
    return t[:cut]

def pass_at_k(n, c, k):
    if n - c < k: return 1.0
    return 1.0 - float(np.prod(1.0 - k/np.arange(n-c+1, n+1)))

def main(n=5, temp=0.6, limit=None, model_name="Salesforce/codegen-350M-mono"):
    set_seed(1234)
    tok = AutoTokenizer.from_pretrained(model_name); tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16).to("cuda").eval()
    model.config.pad_token_id = tok.eos_token_id

    problems = [{"task_id": r["task_id"], "prompt": r["prompt"], "test": r["test"],
                  "entry_point": r["entry_point"]}
                for r in load_dataset("openai/openai_humaneval", split="test")]
    if limit: problems = problems[:limit]

    @torch.no_grad()
    def gen(prompt):
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=1700).to("cuda")
        out = model.generate(**ids, max_new_tokens=256, do_sample=True, temperature=temp,
                              top_p=0.95, num_return_sequences=n, pad_token_id=tok.eos_token_id)
        return [truncate(x) for x in tok.batch_decode(out[:, ids.input_ids.shape[1]:], skip_special_tokens=True)]

    counts, failures = [], Counter()
    for j, prob in enumerate(problems):
        c = 0
        for comp in gen(prob["prompt"]):
            r = check_correctness(prob, comp)
            if r.passed: c += 1
            else: failures[r.outcome.value] += 1
        counts.append(c)
        if (j+1) % 10 == 0:
            print(f"{j+1}/{len(problems)} running pass@1 = {np.mean([pass_at_k(n,cc,1) for cc in counts]):.3f}")

    p1 = float(np.mean([pass_at_k(n,c,1) for c in counts]))
    p5 = float(np.mean([pass_at_k(n,c,5) for c in counts]))
    result = {"model": model_name, "dataset": "humaneval", "n": n, "temperature": temp,
              "num_problems": len(problems), "pass@1": round(p1,4), "pass@5": round(p5,4),
              "failure_modes": dict(failures)}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(result, open(os.path.join(HERE, "results/baseline_humaneval_350M_mono.json"), "w"), indent=2)
    print("\n=== FULL BASELINE ===")
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    main()
