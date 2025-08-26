# Use slim Python image
FROM python:3.11-slim

# Disable .pyc + buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m appuser

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Install dependencies using pyproject.toml
COPY services/api/pyproject.toml /app/
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .

# Copy app code
COPY services/api/app /app/app

# Run as non-root user
USER appuser

# Expose port for FastAPI
EXPOSE 8000

# Start with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
