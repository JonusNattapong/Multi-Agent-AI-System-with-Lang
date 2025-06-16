#!/bin/bash
# Quick start script for Multi-Agent AI System

echo "🚀 Multi-Agent AI System - Quick Start"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

# Setup environment
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env file with your API keys before running"
    echo ""
    echo "Required API keys:"
    echo "- OPENAI_API_KEY (required)"
    echo "- LANGCHAIN_API_KEY (optional, for tracing)"
    echo ""
    echo "Edit .env file now? (y/n)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ .env file already exists"
fi

# Create directories
mkdir -p outputs logs data
echo "✅ Created project directories"

# Run a quick test
echo "🧪 Running a quick test..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from config import settings
from utils import get_logger

logger = get_logger('quickstart')
logger.info('Quick start test successful!')

if settings.OPENAI_API_KEY:
    print('✅ OpenAI API key configured')
else:
    print('⚠️  OpenAI API key not configured')

if settings.LANGCHAIN_TRACING_V2:
    print('✅ LangSmith tracing enabled')
else:
    print('ℹ️  LangSmith tracing disabled')
"

echo ""
echo "🎉 Quick start completed!"
echo ""
echo "Next steps:"
echo "1. Make sure your API keys are set in .env"
echo "2. Run the main application:"
echo "   python src/main.py"
echo ""
echo "Or try examples:"
echo "   python examples/basic_multi_agent.py"
echo "   python examples/content_pipeline.py" 
echo "   python examples/research_analysis.py"
echo ""
echo "For help: python src/main.py --help"
