# ═══════════════════════════════════════════════════════════════════════
# Price-My-Car (AutoIntel) — ergonomic Docker entry points
# ═══════════════════════════════════════════════════════════════════════

DOCKER_COMPOSE := docker compose

.PHONY: help up down logs ps build shell test lint health config clean reset

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

up: ## Start the app (dev override with source mounts + hot reload)
	@[ -f users_db.json ] || echo '{"users": {}, "meta": {}}' > users_db.json  # valid JSON so load_users_db() works
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d

down: ## Stop the app
	$(DOCKER_COMPOSE) down

logs: ## Tail app logs
	$(DOCKER_COMPOSE) logs -f --tail=100 app

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

build: ## Build images (dev target)
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build

shell: ## Open a shell in the app container
	$(DOCKER_COMPOSE) exec app /bin/sh

test: ## Run the helper unit tests inside the dev image
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm app python -m pytest test_helpers.py -v --tb=short -x

lint: ## Compile-check all Python files
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm app sh -c "python -m compileall -q streamlit_app.py helpers.py && echo OK"

health: ## Check Streamlit health endpoint
	curl -fsS http://localhost:8501/_stcore/health

config: ## Validate compose files
	$(DOCKER_COMPOSE) config

clean: ## Stop and remove containers + volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans

reset: clean ## Full rebuild from scratch
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d
