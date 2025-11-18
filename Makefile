.PHONY: help build up down logs clean restart migrate seed test

help:
	@echo "Garden Platform - Docker Commands"
	@echo "=================================="
	@echo "make build       - Build all Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make logs        - View logs from all services"
	@echo "make clean       - Remove all containers, volumes, and images"
	@echo "make restart     - Restart all services"
	@echo "make migrate     - Run database migrations"
	@echo "make seed        - Seed database with initial data"
	@echo "make test        - Run backend tests"
	@echo "make prod-up     - Start production services"
	@echo "make prod-down   - Stop production services"

build:
	docker compose build

up:
	docker compose up -d
	@echo "✓ Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost:8000"
	@echo "ML Service: http://localhost:8001"

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi all --remove-orphans
	@echo "✓ Cleaned all containers, volumes, and images"

restart: down up

migrate:
	docker compose exec backend alembic upgrade head
	@echo "✓ Migrations applied"

seed:
	docker compose exec backend python seed_data.py
	@echo "✓ Database seeded"

test:
	docker compose exec backend pytest

prod-up:
	docker compose -f docker-compose.prod.yml up -d --build
	@echo "✓ Production services started"

prod-down:
	docker compose -f docker-compose.prod.yml down

db-shell:
	docker compose exec postgres psql -U garden -d garden_db

backend-shell:
	docker compose exec backend bash

frontend-shell:
	docker compose exec frontend sh

ml-shell:
	docker compose exec ml-service bash
