# Dockerfile for Hugging Face Spaces (Docker SDK)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hf_deploy ./hf_deploy
COPY manifest.yaml .

ENV HF_DEPLOY_ADAPTER_SOURCE=hub
ENV HF_ORG=care2achieve
ENV HF_DEPLOY_EAGER_LOAD=true
ENV HF_DEPLOY_DEVICE=cpu
ENV PYTHONPATH=/app

EXPOSE 7860
CMD ["uvicorn", "hf_deploy.api.app:app", "--host", "0.0.0.0", "--port", "7860"]
