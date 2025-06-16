"""
Configuration settings for the Multi-Agent AI System
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LangSmith Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "multi-agent-system")
      # Local LLM Configuration (Ollama)
    OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4:latest")
    OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "moondream:latest")
    
    # Hugging Face Configuration
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/Phi-4")
    HF_VISION_MODEL = os.getenv("HF_VISION_MODEL", "vikhyatk/moondream2")
    HF_DEVICE = os.getenv("HF_DEVICE", "auto")
    HF_CACHE_DIR = os.getenv("HF_CACHE_DIR", "./models")
    USE_QUANTIZATION = os.getenv("USE_QUANTIZATION", "true").lower() == "true"
    
    # Model Provider Selection
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama")  # ollama, huggingface, openai
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "huggingface")
    
    # Alternative Local LLM Endpoints
    LOCALAI_API_BASE = os.getenv("LOCALAI_API_BASE")
    OPENLLM_API_BASE = os.getenv("OPENLLM_API_BASE")
    
    # Document Intelligence Configuration
    DOC_LOADER_TYPE = os.getenv("DOC_LOADER_TYPE", "docling")
    MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "8192"))
    ENABLE_PII_MASKING = os.getenv("ENABLE_PII_MASKING", "true").lower() == "true"
    DOCUMENT_UPLOAD_PATH = os.getenv("DOCUMENT_UPLOAD_PATH", "./documents")
    EXTRACTED_DATA_PATH = os.getenv("EXTRACTED_DATA_PATH", "./extracted")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model Configuration
    DEFAULT_MODEL = "gpt-4-turbo-preview"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Agent Configuration
    AGENT_CONFIG = {
        "research_agent": {
            "model": DEFAULT_MODEL,
            "temperature": 0.3,
            "max_tokens": MAX_TOKENS,
            "system_prompt": """You are a research specialist AI agent. Your role is to:
            1. Gather comprehensive information on given topics
            2. Analyze and synthesize multiple sources
            3. Provide well-structured research summaries
            4. Identify key insights and trends
            Always be thorough, accurate, and cite your reasoning."""
        },
        "writing_agent": {
            "model": DEFAULT_MODEL,
            "temperature": 0.7,
            "max_tokens": MAX_TOKENS,
            "system_prompt": """You are a professional writing AI agent. Your role is to:
            1. Create engaging, well-structured content
            2. Adapt writing style to target audience
            3. Ensure clarity and readability
            4. Follow best practices for content creation
            Focus on creating compelling, informative content."""
        },
        "review_agent": {
            "model": DEFAULT_MODEL,
            "temperature": 0.2,
            "max_tokens": MAX_TOKENS,
            "system_prompt": """You are a quality assurance AI agent. Your role is to:
            1. Review content for accuracy and quality
            2. Check for grammar, style, and consistency            3. Provide constructive feedback
            4. Ensure content meets specified requirements
            Be thorough and provide specific improvement suggestions."""
        },
        "document_intelligence_agent": {
            "model": f"ollama/{OLLAMA_MODEL}",
            "temperature": 0.1,
            "max_tokens": MAX_CONTEXT_TOKENS,
            "system_prompt": """You are a document intelligence AI agent. Your role is to:
            1. Process and analyze various document types (PDFs, images, text)
            2. Extract structured data from unstructured documents
            3. Classify documents based on content and layout
            4. Handle privacy-sensitive data with PII masking
            5. Work within context window limitations using pagination
            Focus on accuracy, privacy compliance, and efficient processing."""
        }
    }
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        return cls.AGENT_CONFIG.get(agent_name, {})
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set")
            return False
        
        if cls.LANGCHAIN_TRACING_V2 and not cls.LANGCHAIN_API_KEY:
            print("Warning: LangSmith tracing enabled but LANGCHAIN_API_KEY not set")
        
        return True

# Global settings instance
settings = Settings()
