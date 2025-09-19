# LLM-Enhanced Brand Identity Generator - Development Commands

.PHONY: install test lint format type-check clean dev-setup

# Development setup
dev-setup:
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

install:
	pip install -r requirements.txt

# Code quality
lint:
	ruff check brand_identity_generator.py tests/
	black --check brand_identity_generator.py tests/

format:
	black brand_identity_generator.py tests/
	ruff --fix brand_identity_generator.py tests/

type-check:
	mypy brand_identity_generator.py

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=brand_identity_generator --cov-report=html

test-contract:
	pytest tests/contract/ -v

test-integration:
	pytest tests/integration/ -v

test-unit:
	pytest tests/unit/ -v

# Performance testing
test-performance:
	pytest tests/performance/ -v

# Quality gates (run all checks)
quality-check: lint type-check test

# Clean up
clean:
	rm -rf __pycache__/ .pytest_cache/ .coverage htmlcov/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Example runs
example-basic:
	python brand_identity_generator.py examples/basic-brand.md -o output.json

example-enhanced:
	python brand_identity_generator.py examples/basic-brand.md --enhance -o enhanced-output.json

example-gaps:
	python brand_identity_generator.py examples/basic-brand.md --analyze-gaps