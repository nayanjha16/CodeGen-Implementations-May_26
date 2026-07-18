# RepoCoder Studio — inference API + UI
#
# CPU image by default (requirements.txt pulls the CPU build of torch via
# --extra-index-url). For GPU inference: switch the base image to an
# nvidia/cuda devel/runtime image, install a CUDA build of torch instead,
# and add bitsandbytes if you want 4-bit loading (see src/generation_engine.py,
# which already auto-detects torch.cuda.is_available() and only uses 4-bit /
# fp16 when a GPU is present).

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY app/ ./app/

ENV REPOCODER_PROJECT_ROOT=/data
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
