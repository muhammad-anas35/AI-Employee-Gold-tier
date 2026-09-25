# Nexus Task Runner
# Install: cargo install just (or: brew install just)

default: help

# Install dependencies
install:
	pip install -e ".[dev]"

# Install Playwright browsers
playwright:
	playwright install chromium
	playwright install-deps chromium

# Development
dev:
	nexus daemon start --foreground

# Run tests
test:
	pytest tests/ -v

# Code quality
lint:
	ruff check .
	mypy nexus/

format:
	black nexus/
	ruff check . --fix

# Build package
build:
	pip build

# Clean
clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache

# Health check
doctor:
	nexus doctor

# Initialize
init:
	nexus init

# Start daemon
daemon:
	nexus daemon start --foreground

# Status
status:
	nexus status

# Help
help:
	@echo "Nexus Task Runner"
	@echo ""
	@echo "Available commands:"
	@echo "  just install     - Install dependencies"
	@echo "  just playwright  - Install Playwright browsers"
	@echo "  just dev         - Start development daemon"
	@echo "  just test        - Run tests"
	@echo "  just lint        - Run linters"
	@echo "  just format      - Format code"
	@echo "  just build       - Build package"
	@echo "  just clean       - Clean build artifacts"
	@echo "  just doctor      - Run health checks"
	@echo "  just init        - Run setup wizard"
	@echo "  just daemon      - Start daemon"
	@echo "  just status      - Show status"
