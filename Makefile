.PHONY: up down logs test format lint

up: ## Start local stack
	docker compose --env-file .env up -d --build

up-test:
	docker compose --env-file .env.test up -d --build

down:
	docker compose --env-file .env down -v || true
	docker compose --env-file .env.test down -v || true

logs: ## Tail logs
	docker compose logs -f --tail=100

test: ## Run tests (placeholder)
	echo "🧪 Run test logic here (e.g., docker exec api pytest)"

format:
	echo "🧼 Format code with black + ruff"

lint:
	echo "🔍 Run ruff and mypy"

.PHONY: test test-smoke test-contract

test-smoke: ## run only smoke tests (should pass in Step 3)
	. .venv/bin/activate && pytest -q -m smoke

test-contract: ## run contract tests (expected xfail in Step 3)
	. .venv/bin/activate && pytest -q -m contract -rxX

test: ## run all tests
	. .venv/bin/activate && pytest -q