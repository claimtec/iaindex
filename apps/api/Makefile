# Makefile for IA Index Verification API

.PHONY: help install dev prod docker-build docker-up docker-down test lint format clean

help:
	@echo "IA Index Verification API - Available Commands:"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make prod          - Run production server"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean temporary files"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

dev:
	. venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

prod:
	. venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

docker-build:
	docker build -t iaindex-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

test:
	. venv/bin/activate && pytest tests/ -v

lint:
	. venv/bin/activate && flake8 src/
	. venv/bin/activate && pylint src/

format:
	. venv/bin/activate && black src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
