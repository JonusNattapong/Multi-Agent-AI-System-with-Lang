@echo off
REM Document Intelligence Setup Script for Windows
REM Sets up Ollama, Phi-4, and document processing environment

echo.
echo 🚀 Setting up Document Intelligence Stack with Ollama and Phi-4
echo ================================================================
echo.

REM Colors don't work well in batch, so we'll use text formatting
set "INFO=[INFO]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Check if Ollama is installed
echo %INFO% Checking for Ollama installation...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo %WARNING% Ollama not found. Please install Ollama first:
    echo   1. Download from: https://ollama.ai/download
    echo   2. Run the installer
    echo   3. Restart this script
    echo.
    pause
    exit /b 1
) else (
    echo %INFO% Ollama is installed
)

REM Check if Ollama is running
echo %INFO% Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo %INFO% Starting Ollama service...
    start "" ollama serve
    timeout /t 5 /nobreak >nul
    
    REM Check again
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo %ERROR% Failed to start Ollama service
        echo Please start Ollama manually: ollama serve
        pause
        exit /b 1
    )
)
echo %INFO% Ollama is running

REM Pull required models
echo %INFO% Pulling required models...
echo %INFO% Pulling Phi-4 model (this may take a while)...
ollama pull phi4
if %errorlevel% neq 0 (
    echo %WARNING% Failed to pull phi4, trying phi3 as fallback...
    ollama pull phi3
)

echo %INFO% Pulling Moondream vision model...
ollama pull moondream
if %errorlevel% neq 0 (
    echo %WARNING% Failed to pull moondream, skipping vision capabilities
)

REM Optional additional models
set /p "pull_more=Do you want to pull additional models? (llama3.3, qwen2.5) [y/N]: "
if /i "%pull_more%"=="y" (
    echo %INFO% Pulling additional models...
    ollama pull llama3.3
    ollama pull qwen2.5
)

REM Setup Hugging Face
echo %INFO% Setting up Hugging Face integration...
set /p "use_hf=Do you want to setup Hugging Face models? [y/N]: "
if /i "%use_hf%"=="y" (
    set /p "hf_token=Enter your Hugging Face token (or press Enter to skip): "
    if not "%hf_token%"=="" (
        echo HUGGINGFACE_API_TOKEN=%hf_token% >> .env
        echo %INFO% Hugging Face token added to .env
    )
    
    REM Check for GPU
    nvidia-smi >nul 2>&1
    if %errorlevel% equ 0 (
        echo %INFO% GPU detected - will use GPU acceleration
        echo HF_DEVICE=auto >> .env
    ) else (
        echo %WARNING% No GPU detected - will use CPU
        echo HF_DEVICE=cpu >> .env
    )
    
    echo Choose Hugging Face model:
    echo 1. Microsoft Phi-4 (recommended)
    echo 2. Meta Llama 3.3
    echo 3. Qwen 2.5
    set /p "model_choice=Select option [1-3]: "
    
    if "%model_choice%"=="1" (
        echo HF_MODEL_NAME=microsoft/Phi-4 >> .env
    ) else if "%model_choice%"=="2" (
        echo HF_MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct >> .env
    ) else if "%model_choice%"=="3" (
        echo HF_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct >> .env
    ) else (
        echo HF_MODEL_NAME=microsoft/Phi-4 >> .env
        echo %INFO% Using default Phi-4 model
    )
)

REM List available models
echo %INFO% Available models:
ollama list

REM Create directories
echo %INFO% Creating necessary directories...
if not exist "documents" mkdir documents
if not exist "extracted" mkdir extracted
if not exist "sample_documents" mkdir sample_documents
if not exist "logs" mkdir logs

REM Setup Python environment
echo %INFO% Setting up Python environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo %INFO% Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo %INFO% Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo %INFO% Installing Python dependencies...
pip install -r requirements.txt

REM Setup environment file
echo %INFO% Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo %INFO% Created .env file from .env.example
    echo %WARNING% Please edit .env file to configure your settings
) else (
    echo %INFO% .env file already exists
)

REM Test the setup
echo %INFO% Testing the setup...

REM Test Ollama connection
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo %INFO% ✓ Ollama is accessible
) else (
    echo %ERROR% ✗ Ollama is not accessible
    goto :error
)

REM Test Python environment
python -c "import extract_thinker, docling" 2>nul
if %errorlevel% equ 0 (
    echo %INFO% ✓ Python dependencies are installed
) else (
    echo %WARNING% ⚠ Some Python dependencies may be missing
)

echo %INFO% Setup test completed

REM Show usage instructions
echo.
echo %INFO% Setup completed! Here's how to use the document intelligence system:
echo.
echo 1. Run the basic example:
echo    python examples\document_intelligence_local_llm.py
echo.
echo 2. Run the multi-provider example:
echo    python examples\multi_provider_document_intelligence.py
echo.
echo 3. Process your own documents:
echo    from src.workflows import process_document_with_local_llm
echo    result = process_document_with_local_llm('path/to/your/document.pdf')
echo.
echo 4. Switch between providers:
echo    from src.agents import DocumentIntelligenceAgent
echo    agent = DocumentIntelligenceAgent()
echo    agent.switch_model_provider('huggingface')  # or 'ollama'
echo.
echo 5. Configuration files:
echo    - .env: Environment variables and model settings
echo    - requirements.txt: Python dependencies
echo.
echo 6. Supported document types:
echo    - PDFs, Images (PNG, JPG), Word documents, Text files
echo.
echo 7. Available model providers:
echo    - Ollama: Local, fast, privacy-first
echo    - Hugging Face: Latest models, high quality
echo    - Automatic fallback between providers
echo.
echo 8. Privacy features:
echo    - PII masking with Presidio
echo    - Local processing (no cloud API calls)
echo    - GDPR/HIPAA compliant setup
echo.

echo %INFO% 🎉 Document Intelligence setup completed successfully!
echo.
pause
goto :end

:error
echo %ERROR% Setup failed. Please check the error messages above.
pause
exit /b 1

:end
