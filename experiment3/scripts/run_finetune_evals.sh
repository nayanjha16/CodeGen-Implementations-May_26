#!/usr/bin/env bash
# Stage A evals: 30 finetuned cells = 5 models x {finetuned_spider,finetuned_bird,finetuned_combined}
# x {spider,bird} eval datasets. Each finetuned adapter is evaluated on BOTH dev sets
# (in-domain + cross-domain generalization). Sequential (single GPU), resumable (skips
# existing raw cells), adapter-gated (skips if the adapter isn't trained yet).
#
# BIRD evals use dev[:200] (the held-out eval window) — disjoint from every adapter's
# BIRD training data (dev[200:]) and comparable to the zero/one-shot BIRD cells.
set -u
cd /Users/naveensakhamuri/IdeaProjects/Codegen
export HF_HOME=/Users/naveensakhamuri/IdeaProjects/Codegen/models/hf-cache HF_HUB_OFFLINE=1
PY=.venv/bin/python
MODELS=(codegen-350m-multi codet5p-770m qwen3-coder-30b deepseek-coder-33b codestral-22b)
SCENARIOS=(finetuned_spider finetuned_bird finetuned_combined)
DATASETS=(spider bird)

for m in "${MODELS[@]}"; do
  for s in "${SCENARIOS[@]}"; do
    trained_on="${s#finetuned_}"
    adapter="models/${m}-${trained_on}-lora"
    for d in "${DATASETS[@]}"; do
      raw="results/raw/${m}_${s}_${d}.json"
      if [ -f "$raw" ]; then echo "[skip ] $raw (exists)"; continue; fi
      # adapter is trained if EITHER weight form exists (HF: adapter_model / MLX: adapters)
      if [ ! -f "$adapter/adapter_model.safetensors" ] && [ ! -f "$adapter/adapters.safetensors" ]; then
        echo "[MISS ] adapter $adapter not trained — skipping $raw"; continue
      fi
      echo "[eval ] $m / $s / $d  start=$(date '+%H:%M:%S')"
      $PY run_experiments.py --model "$m" --scenario "$s" --dataset "$d" \
          --config experiments/inference.yaml
      echo "[done ] $m / $s / $d  rc=$?  end=$(date '+%H:%M:%S')"
    done
  done
done
echo "EVAL QUEUE COMPLETE $(date '+%H:%M:%S')"
