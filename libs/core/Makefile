# Makefile

# Define the Poetry command for convenience
POETRY := poetry run

# Define targets
.PHONY: all install lint type-check clean help

# Default target: runs both linting and type checking
all: lint type-check

# Install dependencies (if needed)
install:
	poetry install

# Lint the code using Ruff
lint:
	@echo "Running Ruff linter..."
	$(POETRY) ruff check . --fix

	@echo "Running Black code formatter..."
	$(POETRY) black .

# Type check the code using Mypy
type-check:
	@echo "Running Mypy type checks..."
	$(POETRY) mypy .

# Clean up Python cache files
clean:
	@echo "Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -r {} + || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + || true

# Display help information
help:
	@echo "Available make commands:"
	@echo "  make install      Install project dependencies using Poetry."
	@echo "  make lint         Run Ruff linter on the project."
	@echo "  make type-check   Run Mypy type checks on the project."
	@echo "  make all          Run both linting and type checking."
	@echo "  make clean        Remove cache and compiled files."
	@echo "  make help         Show this help message."
