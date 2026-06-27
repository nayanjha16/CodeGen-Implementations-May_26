"""Evaluate the Stage-1 LoRA fine-tuned codegen-350M on HumanEval by execution
accuracy (pass@1/pass@5), using the SAME harness as run_real_baseline.py so the
comparison vs the 0.111 baseline is apples-to-apples.

Run in Colab with a GPU, AFTER run_finetune.py has produced the adapter:
    python Group-30/scripts/eval_finetuned.py                 # seeds 1234,0,42
    python Group-30/scripts/eval_finetuned.py --seeds 1234    # single seed

Writes Group-30/results/finetuned_v2_multiseed.json with per-seed numbers and
mean +/- std, so the lift can't be dismissed as sampling noise.
Measured (seed 1234): pass@1 0.111 -> 0.121, pass@5 0.177 -> 0.207.
"""
import os, sys, json, argparse, importlib.util
import numpy as np
from collections import Counter
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from datasets import load_dataset
from peft import PeftModel

HERE       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Group-30/
ADAPTER    = os.path.join(HERE, "models", "lora_mbpp_v2")
BASE_MODEL = "Salesforce/codegen-350M-mono"
N, TEMP    = 5, 0.6
BASELINE_P1, BASELINE_P5 = 0.111, 0.177

# reuse the EXACT harness helpers from the baseline runner
spec = importlib.util.spec_from_file_location(
    "baseline", os.path.join(HERE, "scripts", "run_real_baseline.py"))
baseline = importlib.util.module_from_spec(spec); sys.modules["baseline"] = baseline
spec.loader.exec_module(baseline)
truncate, pass_at_k, check_correctness = (
    baseline.truncate, baseline.pass_at_k, baseline.check_correctness)


def load_model():
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16)
    model = PeftModel.from_pretrained(base, ADAPTER).merge_and_unload().to("cuda").eval()
    tok = AutoTokenizer.from_pretrained(ADAPTER); tok.pad_token = tok.eos_token
    model.config.pad_token_id = tok.eos_token_id
    return model, tok


def main(seeds):
    model, tok = load_model()
    problems = [{"task_id": r["task_id"], "prompt": r["prompt"], "test": r["test"],
                  "entry_point": r["entry_point"]}
                for r in load_dataset("openai/openai_humaneval", split="test")]

    @torch.no_grad()
    def gen(prompt):
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=1700).to("cuda")
        out = model.generate(**ids, max_new_tokens=256, do_sample=True, temperature=TEMP,
                              top_p=0.95, num_return_sequences=N, pad_token_id=tok.eos_token_id)
        return [truncate(x) for x in
                tok.batch_decode(out[:, ids.input_ids.shape[1]:], skip_special_tokens=True)]

    def run_seed(seed):
        set_seed(seed)
        counts, failures = [], Counter()
        for j, prob in enumerate(problems):
            c = 0
            for comp in gen(prob["prompt"]):
                r = check_correctness(prob, comp)
                if r.passed: c += 1
                else: failures[r.outcome.value] += 1
            counts.append(c)
            if (j + 1) % 20 == 0:
                print(f"  seed {seed}: {j+1}/{len(problems)} "
                      f"running pass@1={np.mean([pass_at_k(N,cc,1) for cc in counts]):.3f}")
        p1 = float(np.mean([pass_at_k(N, c, 1) for c in counts]))
        p5 = float(np.mean([pass_at_k(N, c, 5) for c in counts]))
        print(f"  -> seed {seed}: pass@1={p1:.4f}  pass@5={p5:.4f}  failures={dict(failures)}")
        return p1, p5

    runs = {s: run_seed(s) for s in seeds}
    p1s = np.array([v[0] for v in runs.values()])
    p5s = np.array([v[1] for v in runs.values()])
    summary = {
        "model": "codegen-350M-mono + LoRA(MBPP, HumanEval-shape)",
        "dataset": "humaneval", "n": N, "temperature": TEMP,
        "seeds": list(runs.keys()),
        "pass@1_per_seed": [round(x, 4) for x in p1s.tolist()],
        "pass@5_per_seed": [round(x, 4) for x in p5s.tolist()],
        "pass@1_mean": round(float(p1s.mean()), 4), "pass@1_std": round(float(p1s.std()), 4),
        "pass@5_mean": round(float(p5s.mean()), 4), "pass@5_std": round(float(p5s.std()), 4),
        "baseline_pass@1": BASELINE_P1, "baseline_pass@5": BASELINE_P5,
        "lift_survives_noise": bool(p1s.mean() - p1s.std() > BASELINE_P1),
    }
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(summary, open(os.path.join(HERE, "results/finetuned_v2_multiseed.json"), "w"), indent=2)
    print("\n=== MULTI-SEED SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nBASELINE  pass@1={BASELINE_P1}            pass@5={BASELINE_P5}")
    print(f"v2 FT     pass@1={p1s.mean():.3f}+/-{p1s.std():.3f}   "
          f"pass@5={p5s.mean():.3f}+/-{p5s.std():.3f}")
    print(f"\nLift survives noise (mean-std > baseline)?  {summary['lift_survives_noise']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1234, 0, 42])
    main(ap.parse_args().seeds)
