# Model UI for Codegen-phase2 — text2sql + sql2nosql, Run #2 teacher adapter.
#
# Portable CPU image (runs on any Linux server). For an NVIDIA GPU server, swap
# the base for `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04`, install python +
# a CUDA torch wheel, and run with `--gpus all`; the device selector
# (src/device.py) auto-picks CUDA when present. See docs/DEPLOYMENT.md.
#
# Heavy assets are NOT baked in — mount them at runtime (see docker-compose.yml):
#   /app/models/codegen_pass2_teacher   the trained Run #2 adapter (required)
#   /app/data/spider/database            Spider SQLite DBs (text2sql execution)
#   /root/.cache/huggingface             HF cache for the 1.5B base model
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface \
    PORT=8000

# mongosh client — the NoSQL executor shells out to it (src/mongo_exec.py).
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg ca-certificates \
    && curl -fsSL https://pgp.mongodb.com/server-7.0.asc \
        | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor \
    && echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" \
        > /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update && apt-get install -y --no-install-recommends mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Model stack (CPU torch wheels) + web layer. Torch CPU keeps the image portable;
# override with a CUDA wheel in the GPU image.
COPY requirements.txt requirements-serve.txt ./
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r requirements.txt \
    && pip install -r requirements-serve.txt

# Application code (not the models/data — those are mounted). scripts/ is included
# so `setup_mongo.py` can load DocSpider into the mongo service from this image.
COPY src ./src
COPY app.py run_multi_task_inference.py ./
COPY scripts ./scripts
COPY static ./static

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Lazy-load so the container is healthy before the (slow) first model load; the
# first /api/generate warms it. Set CODEGEN_LAZY_LOAD=0 to load eagerly at boot.
ENV CODEGEN_LAZY_LOAD=1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
