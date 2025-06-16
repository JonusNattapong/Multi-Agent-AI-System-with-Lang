#!/bin/bash

# Document Intelligence Setup Script
# Sets up Ollama, Phi-4, and document processing environment

set -e

echo "🚀 Setting up Document Intelligence Stack with Ollama and Phi-4"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows (Git Bash)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    print_status "Detected Windows environment"
    IS_WINDOWS=true
else
    print_status "Detected Unix-like environment"
    IS_WINDOWS=false
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Ollama is installed
check_ollama() {
    if command_exists ollama; then
        print_status "Ollama is already installed"
        return 0
    else
        return 1
    fi
}

# Function to install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    if [[ "$IS_WINDOWS" == true ]]; then
        print_warning "Please install Ollama manually on Windows:"
        echo "1. Download from: https://ollama.ai/download"
        echo "2. Run the installer"
        echo "3. Restart this script"
        exit 1
    else
        # Unix/Linux/macOS installation
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
}

# Function to start Ollama service
start_ollama() {
    print_status "Starting Ollama service..."
    
    if [[ "$IS_WINDOWS" == true ]]; then
        # On Windows, Ollama usually runs as a service
        print_status "Ollama should start automatically on Windows"
        sleep 3
    else
        # Start Ollama in background
        ollama serve &
        sleep 5
    fi
}

# Function to check if Ollama is running
check_ollama_running() {
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_status "Ollama is running!"
            return 0
        fi
        
        print_warning "Waiting for Ollama to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    print_error "Ollama failed to start or is not accessible"
    return 1
}

# Function to pull required models
pull_models() {
    print_status "Pulling required models..."
    
    # Pull Phi-4 (main model)
    print_status "Pulling Phi-4 model (this may take a while)..."
    if ! ollama pull phi4; then
        print_warning "Failed to pull phi4, trying phi3 as fallback..."
        ollama pull phi3
    fi
    
    # Pull Moondream (vision model)
    print_status "Pulling Moondream vision model..."
    if ! ollama pull moondream; then
        print_warning "Failed to pull moondream, skipping vision capabilities"
    fi
    
    # Optional: Pull other useful models
    read -p "Do you want to pull additional models? (llama3.3, qwen2.5) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Pulling additional models..."
        ollama pull llama3.3 || print_warning "Failed to pull llama3.3"
        ollama pull qwen2.5 || print_warning "Failed to pull qwen2.5"
    fi
}

# Function to setup Hugging Face
setup_huggingface() {
    print_status "Setting up Hugging Face integration..."
    
    # Check if HF token is provided
    read -p "Do you have a Hugging Face token? (recommended for latest models) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Please enter your Hugging Face token (or press Enter to skip):"
        read -s HF_TOKEN
        if [[ -n "$HF_TOKEN" ]]; then
            echo "HUGGINGFACE_API_TOKEN=$HF_TOKEN" >> .env
            print_status "Hugging Face token added to .env"
        fi
    fi
    
    # Check GPU availability
    if command_exists nvidia-smi; then
        print_status "GPU detected - Hugging Face models will use GPU acceleration"
        echo "HF_DEVICE=auto" >> .env
    else
        print_warning "No GPU detected - Hugging Face models will use CPU (slower)"
        echo "HF_DEVICE=cpu" >> .env
    fi
    
    # Ask about model preferences
    echo "Choose Hugging Face model setup:"
    echo "1. Microsoft Phi-4 (recommended, ~14B parameters)"
    echo "2. Meta Llama 3.3 (larger, ~70B parameters)"
    echo "3. Qwen 2.5 (multilingual, various sizes)"
    echo "4. Custom model name"
    read -p "Select option [1-4]: " model_choice
    
    case $model_choice in
        1)
            echo "HF_MODEL_NAME=microsoft/Phi-4" >> .env
            ;;
        2)
            echo "HF_MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct" >> .env
            ;;
        3)
            echo "HF_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct" >> .env
            ;;
        4)
            read -p "Enter custom model name: " custom_model
            echo "HF_MODEL_NAME=$custom_model" >> .env
            ;;
        *)
            echo "HF_MODEL_NAME=microsoft/Phi-4" >> .env
            print_status "Using default Phi-4 model"
            ;;
    esac
    
    print_status "Hugging Face setup completed"
}

# Function to list available models
list_models() {
    print_status "Available models:"
    ollama list
}

# Function to create directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p documents
    mkdir -p extracted
    mkdir -p sample_documents
    mkdir -p logs
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if virtual environment exists
    if [[ ! -d "venv" && ! -d ".venv" ]]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    if [[ "$IS_WINDOWS" == true ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    print_status "Python dependencies installed"
}

# Function to setup environment file
setup_env_file() {
    print_status "Setting up environment configuration..."
    
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        print_status "Created .env file from .env.example"
        print_warning "Please edit .env file to configure your settings"
    else
        print_status ".env file already exists"
    fi
}

# Function to test the setup
test_setup() {
    print_status "Testing the setup..."
    
    # Test Ollama connection
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_status "✓ Ollama is accessible"
    else
        print_error "✗ Ollama is not accessible"
        return 1
    fi
    
    # Test if models are available
    local models=$(ollama list | grep -E "(phi|moondream)" | wc -l)
    if [[ $models -gt 0 ]]; then
        print_status "✓ Required models are available"
    else
        print_warning "⚠ Some required models may be missing"
    fi
    
    # Test Python environment
    if python -c "import extract_thinker, docling" 2>/dev/null; then
        print_status "✓ Python dependencies are installed"
    else
        print_warning "⚠ Some Python dependencies may be missing"
    fi
    
    print_status "Setup test completed"
}

# Function to show usage instructions
show_usage() {
    echo
    print_status "Setup completed! Here's how to use the document intelligence system:"
    echo
    echo "1. Run the basic example:"
    echo "   python examples/document_intelligence_local_llm.py"
    echo
    echo "2. Run the multi-provider example:"
    echo "   python examples/multi_provider_document_intelligence.py"
    echo
    echo "3. Process your own documents:"
    echo "   from src.workflows import process_document_with_local_llm"
    echo "   result = process_document_with_local_llm('path/to/your/document.pdf')"
    echo
    echo "4. Switch between providers:"
    echo "   from src.agents import DocumentIntelligenceAgent"
    echo "   agent = DocumentIntelligenceAgent()"
    echo "   agent.switch_model_provider('huggingface')  # or 'ollama'"
    echo
    echo "5. Configuration files:"
    echo "   - .env: Environment variables and model settings"
    echo "   - requirements.txt: Python dependencies"
    echo
    echo "6. Supported document types:"
    echo "   - PDFs, Images (PNG, JPG), Word documents, Text files"
    echo
    echo "7. Available model providers:"
    echo "   - Ollama: Local, fast, privacy-first"
    echo "   - Hugging Face: Latest models, high quality"
    echo "   - Automatic fallback between providers"
    echo
    echo "8. Privacy features:"
    echo "   - PII masking with Presidio"
    echo "   - Local processing (no cloud API calls)"
    echo "   - GDPR/HIPAA compliant setup"
    echo
}

# Main setup function
main() {
    print_status "Starting Document Intelligence setup..."
    
    # Check and install Ollama
    if ! check_ollama; then
        install_ollama
    fi
    
    # Start Ollama service
    start_ollama
    
    # Check if Ollama is running
    if ! check_ollama_running; then
        print_error "Cannot proceed without Ollama running"
        exit 1
    fi
    
    # Pull required models
    pull_models
    
    # Setup Hugging Face
    setup_huggingface
    
    # List available models
    list_models
    
    # Create directories
    create_directories
    
    # Install Python dependencies
    install_python_deps
    
    # Setup environment file
    setup_env_file
    
    # Test the setup
    test_setup
    
    # Show usage instructions
    show_usage
    
    print_status "🎉 Document Intelligence setup completed successfully!"
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@"
