.PHONY: up down logs ingest test migrate revision mcp fmt help

help:
	@echo "MarketLens — make targets"
	@echo "  up       docker compose up --build (db, ollama, backend, frontend)"
	@echo "  ingest   run the one-shot ingest (SEC filings + news + seed portfolio)"
	@echo "  down     stop the stack"
	@echo "  logs     tail backend logs"
	@echo "  test     run the backend test suite"
	@echo "  migrate  apply DB migrations"
	@echo "  revision alembic autogenerate (m=\"message\")"
	@echo "  mcp      run the MCP server entrypoint (stdio, for Claude/Cursor)"
	@echo "  fmt      ruff format + autofix"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend

ingest:
	docker compose run --rm ingest

test:
	cd backend && pytest -q

migrate:
	cd backend && alembic upgrade head

revision:
	cd backend && alembic revision --autogenerate -m "$(m)"

mcp:
	cd backend && python -m mcp_server.server

fmt:
	cd backend && ruff check --fix . && ruff format .
