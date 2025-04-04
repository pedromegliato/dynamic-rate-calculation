.PHONY: install test lint format clean run docker-build docker-up docker-down

# Instalação
install:
	pip install -r requirements.txt
	pre-commit install

# Testes
test:
	pytest

# Linting
lint:
	flake8
	mypy .

# Formatação
format:
	black .
	isort .

# Limpeza
clean:
	find . -type d -name "__pycache__" -o -name "*.egg-info" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name "htmlcov" -o -name "dist" -o -name "build" | xargs rm -rf
	find . -type f -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" -o -name ".coverage" | xargs rm -f

# Execução
run:
	uvicorn main:app --reload

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Tudo
all: install lint test format 