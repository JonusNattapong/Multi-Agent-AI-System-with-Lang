"""
Unified Model Manager for Ollama and Hugging Face models
"""
import os
import logging
from typing import Dict, Any, Optional, Union, List
from abc import ABC, abstractmethod

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import ollama

from ..config.settings import settings

logger = logging.getLogger(__name__)

class BaseModelProvider(ABC):
    """Abstract base class for model providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass

class OllamaProvider(BaseModelProvider):
    """Ollama model provider"""
    
    def __init__(self, model_name: str = None, api_base: str = None):
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.api_base = api_base or settings.OLLAMA_API_BASE
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Ollama client"""
        try:
            # Set Ollama API base if different from default
            if self.api_base != "http://localhost:11434":
                os.environ["OLLAMA_HOST"] = self.api_base
            
            self.client = ollama.Client(host=self.api_base)
            logger.info(f"Initialized Ollama provider with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            self.client = None
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        if not self.client:
            raise RuntimeError("Ollama client not available")
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 2048)
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            if not self.client:
                return False
            
            # Try to list models to check connection
            models = self.client.list()
            model_names = [model['name'] for model in models.get('models', [])]
            return any(self.model_name in name for name in model_names)
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information"""
        try:
            if not self.client:
                return {"status": "unavailable", "error": "Client not initialized"}
            
            models = self.client.list()
            for model in models.get('models', []):
                if self.model_name in model['name']:
                    return {
                        "provider": "ollama",
                        "name": model['name'],
                        "size": model.get('size', 'unknown'),
                        "modified": model.get('modified_at', 'unknown'),
                        "status": "available"
                    }
            
            return {"status": "model_not_found", "model": self.model_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

class HuggingFaceProvider(BaseModelProvider):
    """Hugging Face model provider"""
    
    def __init__(self, model_name: str = None, device: str = None):
        self.model_name = model_name or settings.HF_MODEL_NAME
        self.device = device or settings.HF_DEVICE
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Hugging Face model and tokenizer"""
        try:
            logger.info(f"Loading Hugging Face model: {self.model_name}")
            
            # Setup quantization if enabled
            quantization_config = None
            if settings.USE_QUANTIZATION and torch.cuda.is_available():
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                logger.info("Using 4-bit quantization")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.HF_CACHE_DIR,
                token=settings.HUGGINGFACE_API_TOKEN
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map=self.device if self.device != "auto" else "auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                cache_dir=settings.HF_CACHE_DIR,
                token=settings.HUGGINGFACE_API_TOKEN,
                trust_remote_code=True
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.device if self.device != "auto" else "auto"
            )
            
            logger.info("Hugging Face model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face provider: {e}")
            self.tokenizer = None
            self.model = None
            self.pipeline = None
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Hugging Face model"""
        if not self.pipeline:
            raise RuntimeError("Hugging Face model not available")
        
        try:
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            return outputs[0]['generated_text'].strip()
            
        except Exception as e:
            logger.error(f"Hugging Face generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Hugging Face model is available"""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Hugging Face model information"""
        if not self.model:
            return {"status": "unavailable", "error": "Model not loaded"}
        
        try:
            return {
                "provider": "huggingface",
                "name": self.model_name,
                "device": str(self.model.device) if hasattr(self.model, 'device') else self.device,
                "dtype": str(self.model.dtype) if hasattr(self.model, 'dtype') else "unknown",
                "quantized": settings.USE_QUANTIZATION,
                "status": "available"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

class UnifiedModelManager:
    """Unified manager for both Ollama and Hugging Face models"""
    
    def __init__(self):
        self.providers = {}
        self.active_provider = None
        self.fallback_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        logger.info("Initializing model providers...")
        
        # Initialize Ollama provider
        try:
            ollama_provider = OllamaProvider()
            if ollama_provider.is_available():
                self.providers["ollama"] = ollama_provider
                logger.info("Ollama provider initialized and available")
            else:
                logger.warning("Ollama provider not available")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
        
        # Initialize Hugging Face provider
        try:
            hf_provider = HuggingFaceProvider()
            if hf_provider.is_available():
                self.providers["huggingface"] = hf_provider
                logger.info("Hugging Face provider initialized and available")
            else:
                logger.warning("Hugging Face provider not available")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face provider: {e}")
        
        # Set active and fallback providers
        self._set_active_provider()
    
    def _set_active_provider(self):
        """Set active and fallback providers based on configuration"""
        primary = settings.MODEL_PROVIDER
        fallback = settings.FALLBACK_PROVIDER
        
        if primary in self.providers:
            self.active_provider = self.providers[primary]
            logger.info(f"Set primary provider: {primary}")
        else:
            logger.warning(f"Primary provider {primary} not available")
        
        if fallback in self.providers and fallback != primary:
            self.fallback_provider = self.providers[fallback]
            logger.info(f"Set fallback provider: {fallback}")
        
        # If no primary provider, use any available
        if not self.active_provider and self.providers:
            provider_name = list(self.providers.keys())[0]
            self.active_provider = self.providers[provider_name]
            logger.info(f"Using available provider: {provider_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using active provider with fallback"""
        if not self.active_provider:
            raise RuntimeError("No model providers available")
        
        try:
            return self.active_provider.generate(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Primary provider failed: {e}")
            
            if self.fallback_provider:
                logger.info("Trying fallback provider...")
                try:
                    return self.fallback_provider.generate(prompt, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback provider also failed: {fallback_error}")
                    raise
            else:
                raise
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        if provider_name in self.providers:
            self.active_provider = self.providers[provider_name]
            logger.info(f"Switched to provider: {provider_name}")
            return True
        else:
            logger.error(f"Provider {provider_name} not available")
            return False
    
    def get_provider_info(self, provider_name: str = None) -> Dict[str, Any]:
        """Get information about a provider"""
        if provider_name:
            if provider_name in self.providers:
                return self.providers[provider_name].get_model_info()
            else:
                return {"status": "not_available", "provider": provider_name}
        else:
            # Return info for all providers
            info = {}
            for name, provider in self.providers.items():
                info[name] = provider.get_model_info()
            return info
    
    def get_active_provider_name(self) -> Optional[str]:
        """Get name of active provider"""
        for name, provider in self.providers.items():
            if provider == self.active_provider:
                return name
        return None

# Global model manager instance
model_manager = UnifiedModelManager()
