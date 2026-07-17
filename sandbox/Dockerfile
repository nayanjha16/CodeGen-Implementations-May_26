FROM python:3.11-slim

RUN groupadd -r sandbox && useradd -r -g sandbox -m sandbox

WORKDIR /app

COPY runner.py /app/runner.py

RUN chown -R sandbox:sandbox /app

USER sandbox

# Resource limits enforced at runtime via docker run flags
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/app/runner.py"]
