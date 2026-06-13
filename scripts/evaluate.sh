#!/usr/bin/env bash
# Run benchmark evaluation on Spider and BirdBench
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

DATASET="${1:-spider}"
SPLIT="${2:-validation}"
MAX_SAMPLES="${MAX_SAMPLES:-10}"

echo "=== CodeGen Evaluation ==="
echo "Dataset: $DATASET | Split: $SPLIT | Max samples: $MAX_SAMPLES"

python -c "
from src.evaluation.benchmark import BenchmarkRunner
from src.utils.config import load_config

config = load_config()
config['evaluation']['max_samples'] = int('${MAX_SAMPLES}')
runner = BenchmarkRunner(config=config)

dataset = '${DATASET}'
if dataset == 'spider':
    result = runner.run_spider('${SPLIT}')
elif dataset == 'bird':
    result = runner.run_bird('${SPLIT}')
else:
    raise ValueError(f'Unknown dataset: {dataset}')

print('Metrics:', result['metrics'])
print('MLflow run:', result['mlflow_run_id'])
"

echo "Evaluation completed."
