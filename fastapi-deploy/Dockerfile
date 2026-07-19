# Single image for any container host (Google Cloud Run, local Docker, etc.)
# Cloud Run provides HTTPS automatically via *.run.app.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY codegen_api ./codegen_api
COPY manifest.yaml .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# The container has no local models/checkpoints, so pull adapters from the
# Hugging Face Hub (codegenstudio/codegen-350M-*-lora). Override any of these
# with --set-env-vars at deploy time.
ENV CODEGEN_ADAPTER_SOURCE=hub
ENV HF_ORG=codegenstudio
ENV CODEGEN_EAGER_LOAD=true
ENV CODEGEN_DEVICE=cpu
ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
