.PHONY: help build up down restart logs test clean migrate shell test-unit test-e2e test-all test-coverage

help:
	@echo "Available commands:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run Django unit tests"
	@echo "  make test-e2e       - Run Selenium E2E tests"
	@echo "  make test-all       - Run all tests (unit + E2E)"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make shell          - Open Django shell"
	@echo "  make clean          - Remove all containers, volumes, and images"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	@echo "Running backend tests..."
	docker-compose exec backend pytest
	@echo "Running ML service tests..."
	docker-compose exec ml_service pytest

test-unit:
	@echo "Running Django unit tests..."
	cd backend && python manage.py test predictions.test_patients predictions.test_chat predictions.test_treatments predictions.tests

test-e2e:
	@echo "Running Selenium E2E tests..."
	cd tests && python -m pytest e2e/ -v

test-all: test-unit test-e2e
	@echo "All tests completed!"

test-coverage:
	@echo "Running tests with coverage..."
	cd backend && coverage run --source='.' manage.py test
	cd backend && coverage report
	cd backend && coverage html
	@echo "Coverage report generated in backend/htmlcov/index.html"

migrate:
	docker-compose exec backend python manage.py migrate

shell:
	docker-compose exec backend python manage.py shell

clean:
	docker-compose down -v --rmi all

health:
	@echo "Checking backend health..."
	@curl -s http://localhost:8000/api/v1/health/ | python -m json.tool || echo "Backend is down"
	@echo "\nChecking ML service health..."
	@curl -s http://localhost:5001/health/ | python -m json.tool || echo "ML service is down"
	@echo "\nChecking frontend..."
	@curl -s -o /dev/null -w "Frontend status: %{http_code}\n" http://localhost:80 || echo "Frontend is down"

dev:
	docker-compose up --build

prod:
	docker-compose -f docker-compose.yml up -d --build

check-s3:
	@echo "Checking S3 configuration..."
	@docker-compose exec backend python test_s3_connection.py
