# RepoCoder Studio inference API + browser UI.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential curl git openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 repocoder \
    && mkdir -p /data /home/repocoder/.cache \
    && chown -R repocoder:repocoder /data /home/repocoder

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY pyproject.toml ./pyproject.toml

# Curated runtime artifacts only: no training checkpoints or raw datasets.
COPY --chown=repocoder:repocoder repo_explorer_data/ /data/repo_explorer_data/
COPY --chown=repocoder:repocoder outputs/adapters/ /data/outputs/adapters/
COPY --chown=repocoder:repocoder outputs/approved_corpus/ /data/outputs/approved_corpus/
COPY --chown=repocoder:repocoder outputs/corpus_index/ /data/outputs/corpus_index/
COPY --chown=repocoder:repocoder outputs/repositories/ /data/outputs/repositories/

# The production image must contain the validated RAG-aware adapter. Do not
# silently deploy a baseline-only service or fall back to the older adapter.
RUN test -s /data/outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_3_transform/adapter_model.safetensors \
    && test -s /data/outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_3_transform/trained_model_manifest.json

RUN pip install --no-cache-dir --no-deps .

ENV REPOCODER_PROJECT_ROOT=/data \
    REPOCODER_ADAPTER_NAME=RepoCoderStudio_RAGAware_LoRA_v1_3_transform \
    REPOCODER_PROMPT_VERSION=rag_prompt_contract_v1.3_transform \
    REPOCODER_TRAINING_MANIFEST_VERSION=training_manifest_rag_v1.3_transform \
    REPOCODER_TRAINING_DATASET_FILENAME=task_dataset_rag_transform_v1_3.jsonl \
    REPOCODER_MAX_CONTEXT_CHARS=2000 \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    REPOCODER_PROFILE=production \
    REPOCODER_ALLOW_MOCK_EMBEDDINGS=false \
    REPOCODER_AUTO_DOWNLOAD_PUBLIC_REPOS=true \
    HF_HOME=/home/repocoder/.cache/huggingface

USER repocoder
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
  CMD curl --fail --silent http://127.0.0.1:${PORT:-8000}/api/health || exit 1

# PORT is supplied by Cloud Run and similar platforms; 8000 is the local default.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
