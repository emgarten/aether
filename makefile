.PHONY: lint isort black flake8

# Define the lint target
lint: isort black flake8

# Individual commands for formatting and linting
isort:
	isort .

black:
	black .

flake8:
	flake8 .
