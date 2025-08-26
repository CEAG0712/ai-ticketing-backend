# Base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN useradd -m appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY services/worker/pyproject.toml /app/
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .

COPY services/worker/worker /app/worker

USER appuser

# Replace this with actual entrypoint in Step 4
CMD ["python", "-m", "worker.main"]
