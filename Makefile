.PHONY: up down logs test format lint

up: ## Start local stack
	docker compose --env-file .env up -d --build

down: ## Stop all containers
	docker compose --env-file .env down -v

logs: ## Tail logs
	docker compose logs -f --tail=100

test: ## Run tests (placeholder)
	echo "🧪 Run test logic here (e.g., docker exec api pytest)"

format:
	echo "🧼 Format code with black + ruff"

lint:
	echo "🔍 Run ruff and mypy"
