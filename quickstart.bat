@echo off
REM Quick start script for Windows

echo 🚀 Multi-Agent AI System - Quick Start
echo ======================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

REM Setup environment
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file
    echo ⚠️  Please edit .env file with your API keys before running
    echo.
    echo Required API keys:
    echo - OPENAI_API_KEY (required)
    echo - LANGCHAIN_API_KEY (optional, for tracing)
    echo.
    set /p edit_env="Edit .env file now? (y/n): "
    if /i "%edit_env%"=="y" (
        notepad .env
    )
) else (
    echo ✅ .env file already exists
)

REM Create directories
mkdir outputs 2>nul
mkdir logs 2>nul
mkdir data 2>nul
echo ✅ Created project directories

REM Run a quick test
echo 🧪 Running a quick test...
python -c "import sys; sys.path.insert(0, 'src'); from config import settings; from utils import get_logger; logger = get_logger('quickstart'); logger.info('Quick start test successful!'); print('✅ OpenAI API key configured' if settings.OPENAI_API_KEY else '⚠️  OpenAI API key not configured'); print('✅ LangSmith tracing enabled' if settings.LANGCHAIN_TRACING_V2 else 'ℹ️  LangSmith tracing disabled')"

echo.
echo 🎉 Quick start completed!
echo.
echo Next steps:
echo 1. Make sure your API keys are set in .env
echo 2. Run the main application:
echo    python src/main.py
echo.
echo Or try examples:
echo    python examples/basic_multi_agent.py
echo    python examples/content_pipeline.py
echo    python examples/research_analysis.py
echo.
pause
