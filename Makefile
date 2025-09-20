# Facebook Ads Repository - Development Commands for All Agents

.PHONY: install test lint format type-check clean dev-setup test-all

# Development setup
dev-setup:
	pip install -r requirements.txt --user
	pip install pre-commit
	pre-commit install

install:
	pip install -r requirements.txt

# Code quality - all agents
lint:
	ruff check agents/ tests/
	black --check agents/ tests/

format:
	black agents/ tests/
	ruff --fix agents/ tests/

type-check:
	mypy agents/brand_identity_generator/brand_identity_generator.py
	mypy agents/customer_journey_mapper/customer_journey_mapper.py
	mypy agents/constitutional_compliance_validator/constitutional_compliance_validator.py

# Testing - all agents and shared tests
test:
	pytest tests/ agents/ -v

test-all:
	pytest tests/ agents/*/tests/ -v

test-coverage:
	pytest tests/ agents/ --cov=agents --cov-report=html

# Agent-specific testing
test-brand:
	pytest agents/brand_identity_generator/tests/ -v

test-journey:
	pytest agents/customer_journey_mapper/tests/ -v

test-constitutional:
	pytest agents/constitutional_compliance_validator/tests/ -v

# Test types - across all agents
test-contract:
	pytest tests/contract/ agents/*/tests/contract/ -v

test-integration:
	pytest tests/integration/ agents/*/tests/integration/ -v

test-unit:
	pytest tests/unit/ agents/*/tests/unit/ -v

# Performance testing
test-performance:
	pytest tests/performance/ agents/*/tests/performance/ -v

# Quality gates (run all checks)
quality-check: lint type-check test

# Clean up
clean:
	rm -rf __pycache__/ .pytest_cache/ .coverage htmlcov/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find agents/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Example runs - Brand Identity Generator
example-basic:
	python agents/brand_identity_generator/brand_identity_generator.py agents/brand_identity_generator/examples/basic-brand.md -o output.json

example-enhanced:
	python agents/brand_identity_generator/brand_identity_generator.py agents/brand_identity_generator/examples/basic-brand.md --enhance -o enhanced-output.json

example-gaps:
	python agents/brand_identity_generator/brand_identity_generator.py agents/brand_identity_generator/examples/basic-brand.md --analyze-gaps

# Example runs - Customer Journey Mapper
example-journey-ecommerce:
	python agents/customer_journey_mapper/customer_journey_mapper.py --market-description "Eco-conscious millennials interested in sustainable fashion" --industry ecommerce

example-journey-saas:
	python agents/customer_journey_mapper/customer_journey_mapper.py --market-description "Small business owners looking for accounting software solutions" --industry saas

# Example runs - Constitutional Compliance Validator
example-validate-brand:
	python agents/constitutional_compliance_validator/constitutional_compliance_validator.py --file-path agents/brand_identity_generator/brand_identity_generator.py

example-validate-journey:
	python agents/constitutional_compliance_validator/constitutional_compliance_validator.py --file-path agents/customer_journey_mapper/customer_journey_mapper.py