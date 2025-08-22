# Makefile
.PHONY: help install migrate seed test run docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Load seed data"
	@echo "  test        - Run tests"
	@echo "  run         - Run development server"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"
	@echo "  clean       - Clean up generated files"

install:
	pip install -r requirements.txt

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

seed:
	python3 manage.py seed_data

test:
	python3 manage.py test

run:
	python3 manage.py runserver

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage
	rm -f db.sqlite3