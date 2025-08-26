# AI Ticketing Backend

This is the backend system for an AI-powered ticket classification service. It includes:

- A FastAPI service for ingesting tickets (`/ticket`)
- A background worker for classifying tickets via LLM
- Redis (for job queueing)
- MongoDB (for ticket persistence)

## 🐳 Quickstart

```bash
cp .env.example .env
make up

Then POST a ticket:

curl -X POST http://localhost:8000/ticket \
  -H "Content-Type: application/json" \
  -d '{"subject": "Refund request", "description": "Charged twice"}'

📦 Repo Structure
services/
  api/        # FastAPI application
  worker/     # Background job consumer
tests/        # E2E and unit tests

🔧 Requirements

Docker Desktop

make

GitHub CLI (for setup)

🧪 Running tests
make test
