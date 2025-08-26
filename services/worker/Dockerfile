FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN useradd -m appuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# IMPORTANT: copy code BEFORE installing editable package
COPY pyproject.toml /app/
COPY worker /app/worker

RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .

USER appuser
CMD ["python", "-m", "worker.main"]
