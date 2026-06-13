#!/usr/bin/env bash
# CodeGen reproducibility script - fine-tuning placeholder
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

echo "=== CodeGen Training Script ==="
echo "Note: This project evaluates pre-trained CodeGen-350M-Multi."
echo "For fine-tuning, extend this script with your training loop."

python -c "
from src.utils.config import load_config
from src.utils.seeds import set_seeds

config = load_config()
set_seeds(config)
print('Seeds set:', config['seeds'])
print('Model:', config['model']['name'])
print('Training configuration ready.')
"

echo "Training script completed."
