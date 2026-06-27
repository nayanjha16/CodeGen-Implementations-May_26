#!/usr/bin/env bash
# Stage A: train all 15 LoRA adapters (5 models x {spider,bird,combined}) at --train-size 1000.
# Sequential (single Apple GPU). Resumable: skips any adapter whose final weights already exist.
# HF-fast models first (codegen, codet5p) as a real-scale canary before the long MLX block.
set -u
cd /Users/naveensakhamuri/IdeaProjects/Codegen
export HF_HOME=/Users/naveensakhamuri/IdeaProjects/Codegen/models/hf-cache HF_HUB_OFFLINE=1
PY=.venv/bin/python
TS=1000
MODELS=(codegen-350m-multi codet5p-770m qwen3-coder-30b deepseek-coder-33b codestral-22b)
DATASETS=(spider bird combined)

for m in "${MODELS[@]}"; do
  for d in "${DATASETS[@]}"; do
    out="models/${m}-${d}-lora"
    # final weights: HF/seq2seq -> adapter_model.safetensors ; MLX -> adapters.safetensors.
    # Skip if EITHER exists (a model uses one form OR the other, never both).
    if [ -f "$out/adapter_model.safetensors" ] || [ -f "$out/adapters.safetensors" ]; then
      echo "[skip ] $out (already trained)"; continue
    fi
    echo "[train] $m / $d  start=$(date '+%H:%M:%S')"
    $PY run_experiments.py --finetune --model "$m" --dataset "$d" --train-size "$TS" \
        --config experiments/inference.yaml
    rc=$?
    echo "[done ] $m / $d  rc=$rc  end=$(date '+%H:%M:%S')"
    if [ $rc -ne 0 ]; then echo "[ERROR] $m / $d failed (rc=$rc) — continuing queue"; fi
  done
done
echo "QUEUE COMPLETE $(date '+%H:%M:%S')"
