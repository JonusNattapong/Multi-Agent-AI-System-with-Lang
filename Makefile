# Makefile for Multi-Agent AI System

.PHONY: help install test clean run examples docs setup

# Default target
help:
	@echo "Multi-Agent AI System - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup     - Run complete setup process"
	@echo "  install   - Install Python dependencies"
	@echo "  env       - Create .env file from template"
	@echo ""
	@echo "Development:"
	@echo "  test      - Run test suite"
	@echo "  clean     - Clean generated files"
	@echo "  lint      - Run code linting (if available)"
	@echo ""
	@echo "Running:"
	@echo "  run       - Run main application"
	@echo "  demo      - Run all demos"
	@echo "  examples  - List available examples"
	@echo ""
	@echo "Examples:"
	@echo "  basic     - Run basic multi-agent example"
	@echo "  content   - Run content creation pipeline"
	@echo "  research  - Run research analysis example"

# Setup and Installation
setup:
	@echo "🚀 Running complete setup..."
	python setup.py

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

env:
	@echo "⚙️ Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env with your API keys"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

# Development
test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v

clean:
	@echo "🧹 Cleaning generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf outputs/* logs/* data/*
	@echo "✅ Cleanup completed"

lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ tests/ examples/; \
	else \
		echo "⚠️  flake8 not installed. Install with: pip install flake8"; \
	fi

# Running
run:
	@echo "🏃 Running main application..."
	cd src && python main.py

demo:
	@echo "🎬 Running all demos..."
	cd src && python main.py all

examples:
	@echo "📚 Available examples:"
	@echo "  make basic     - Basic multi-agent interaction"
	@echo "  make content   - Content creation pipeline" 
	@echo "  make research  - Research analysis workflow"

# Example commands
basic:
	@echo "🤖 Running basic multi-agent example..."
	python examples/basic_multi_agent.py

content:
	@echo "📝 Running content creation pipeline..."
	python examples/content_pipeline.py

research:
	@echo "🔬 Running research analysis example..."
	python examples/research_analysis.py

# Development shortcuts
dev: install env
	@echo "🛠️ Development environment ready!"

quick-test:
	@echo "⚡ Running quick tests..."
	python -m pytest tests/test_agents.py -v

full-test: test
	@echo "✅ Full test suite completed"

# Documentation (if you add docs later)
docs:
	@echo "📖 Documentation commands:"
	@echo "  README.md contains the main documentation"
	@echo "  Code is documented with docstrings"

# Installation verification
verify:
	@echo "🔍 Verifying installation..."
	@echo "Python version:"
	@python --version
	@echo ""
	@echo "Required packages:"
	@python -c "import langgraph, langchain, langsmith, dotenv; print('✅ All packages available')" || echo "❌ Missing packages"
	@echo ""
	@echo "Environment file:"
	@if [ -f .env ]; then echo "✅ .env exists"; else echo "❌ .env missing"; fi

# Development tools
format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black src/ tests/ examples/; \
		echo "✅ Code formatted with black"; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi

check: lint test
	@echo "✅ Code check completed"

# Quick start for new users
quickstart: setup verify
	@echo ""
	@echo "🎉 Quick start completed!"
	@echo ""
	@echo "Try running:"
	@echo "  make run      # Interactive demo"
	@echo "  make basic    # Basic example" 
	@echo "  make content  # Content pipeline"
	@echo ""

# Show project structure
structure:
	@echo "📁 Project structure:"
	@echo ""
	@tree -I '__pycache__|*.pyc|.git|.env' -a || ls -la
