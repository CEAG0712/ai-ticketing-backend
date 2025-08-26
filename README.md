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
