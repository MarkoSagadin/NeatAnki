.PHONY: dev build assets test

# Set up development environment: install deps + build assets
dev: assets

# Sync dependencies and build frontend assets
assets:
	uv sync
	uv run python build_assets.py

# Build sdist and wheel
build: assets
	uv build

# Run tests
test:
	uv run pytest
