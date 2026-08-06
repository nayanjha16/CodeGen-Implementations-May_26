#!/usr/bin/env bash
# Download all datasets required for NL2Py and Java2Py fine-tuning.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${SCRIPT_DIR}/../raw"
mkdir -p "${RAW_DIR}"

echo "==> Downloading datasets into ${RAW_DIR}"

# --- Spider (text-to-SQL benchmark, used for NL queries) ---
SPIDER_DIR="${RAW_DIR}/spider"
if [ ! -d "${SPIDER_DIR}" ]; then
    echo "Downloading Spider dataset..."
    mkdir -p "${SPIDER_DIR}"
    curl -L -o "${SPIDER_DIR}/spider.zip" \
        "https://yale-lily.github.io/spider/spider.zip" || \
    curl -L -o "${SPIDER_DIR}/spider.zip" \
        "https://drive.google.com/uc?export=download&id=1iRDVHLRCiA6REIXaE-_jn3e9i5XSZaZM"
    unzip -q -o "${SPIDER_DIR}/spider.zip" -d "${SPIDER_DIR}" || true
    echo "Spider download complete."
else
    echo "Spider already present, skipping."
fi

# --- BirdBench (text-to-SQL, more complex) ---
BIRD_DIR="${RAW_DIR}/bird"
if [ ! -d "${BIRD_DIR}" ]; then
    echo "Downloading BirdBench dataset..."
    mkdir -p "${BIRD_DIR}"
    curl -L -o "${BIRD_DIR}/bird.zip" \
        "https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip" || \
    echo "BirdBench: manual download may be required from https://bird-bench.github.io/"
    if [ -f "${BIRD_DIR}/bird.zip" ]; then
        unzip -q -o "${BIRD_DIR}/bird.zip" -d "${BIRD_DIR}" || true
    fi
    echo "BirdBench download attempted."
else
    echo "BirdBench already present, skipping."
fi

# --- CoDocBench (Java-Python translation pairs) ---
CODOC_DIR="${RAW_DIR}/codocbench"
if [ ! -d "${CODOC_DIR}/.git" ]; then
    echo "Cloning CoDocBench..."
    git clone --depth 1 https://github.com/kunpai/codocbench.git "${CODOC_DIR}" || \
    echo "CoDocBench: clone failed — download manually from https://github.com/kunpai/codocbench"
else
    echo "CoDocBench already present, skipping."
fi

# --- CodeParrot, BigQuery/Python, Pile via HuggingFace (handled in preprocess scripts) ---
echo ""
echo "==> HuggingFace datasets (CodeParrot, BigQuery/Python) are fetched during preprocessing."
echo "    Run: python data/scripts/preprocess_nl2py.py"
echo "    Run: python data/scripts/preprocess_java2py.py"
echo ""
echo "Download script finished."
