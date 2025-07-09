.PHONY: test test-cov install dev-install clean lint format

# Install project dependencies
install:
	uv sync

# Install development dependencies
dev-install:
	uv sync --group dev

# Run tests
test:
	uv run pytest tests

# Run tests with coverage
test-cov:
	uv run pytest tests --cov=tmux-capture --cov-report=term-missing --cov-report=html:htmlcov

# Run linting
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format tests tmux-capture

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Run all checks (lint + test)
check: lint test

# Default target
all: dev-install test
