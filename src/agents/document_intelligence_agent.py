"""
Document Intelligence Agent for processing and extracting data from documents
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from extract_thinker import (
    Extractor,
    Process,
    Classification,
    SplittingStrategy,
    CompletionStrategy,
    DocumentLoaderDocling,
    DocumentLoaderMarkItDown,
    ImageSplitter,
    TextSplitter
)
from extract_thinker.models.contract import Contract
from pydantic import Field, BaseModel

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from .base_agent import BaseAgent
from ..config.settings import settings
from ..utils.model_manager import model_manager

# Document contracts for structured extraction
class InvoiceContract(Contract):
    """Contract for invoice documents"""
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: str = Field(description="Date of the invoice")
    total_amount: float = Field(description="Overall total amount")
    vendor_name: str = Field(description="Name of the vendor/supplier")
    customer_name: str = Field(description="Name of the customer/buyer")
    line_items: List[Dict[str, Any]] = Field(description="List of invoice line items", default=[])

class DriverLicenseContract(Contract):
    """Contract for driver license documents"""
    name: str = Field(description="Full name on the license")
    age: int = Field(description="Age of the license holder")
    license_number: str = Field(description="License number")
    expiration_date: str = Field(description="License expiration date")
    state: str = Field(description="Issuing state")
    address: str = Field(description="Address on license")

class PassportContract(Contract):
    """Contract for passport documents"""
    name: str = Field(description="Full name on passport")
    passport_number: str = Field(description="Passport number")
    nationality: str = Field(description="Nationality")
    date_of_birth: str = Field(description="Date of birth")
    expiration_date: str = Field(description="Passport expiration date")
    issuing_country: str = Field(description="Country that issued the passport")

class BusinessCardContract(Contract):
    """Contract for business card documents"""
    name: str = Field(description="Person's name")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    address: str = Field(description="Business address")

class DocumentIntelligenceAgent(BaseAgent):
    """Agent for processing documents and extracting structured data"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.analyzer = None
        self.anonymizer = None
        self.document_loader = None
        self.extractor = None
        self.process = None
        
        # Document classifications
        self.classifications = [
            Classification(
                name="Invoice",
                description="This is an invoice document with billing information",
                contract=InvoiceContract
            ),
            Classification(
                name="Driver License",
                description="This is a driver license document with personal identification",
                contract=DriverLicenseContract
            ),
            Classification(
                name="Passport",
                description="This is a passport document with travel identification",
                contract=PassportContract
            ),
            Classification(
                name="Business Card",
                description="This is a business card with contact information",
                contract=BusinessCardContract
            )        ]
        
        self._initialize_components()

    def _initialize_components(self):
        """Initialize document processing components"""
        try:
            # Initialize PII masking if enabled
            if settings.ENABLE_PII_MASKING:
                self.analyzer = AnalyzerEngine()
                self.anonymizer = AnonymizerEngine()
                self.logger.info("PII masking enabled")
            
            # Initialize document loader
            if settings.DOC_LOADER_TYPE.lower() == "docling":
                self.document_loader = DocumentLoaderDocling()
                self.logger.info("Using Docling document loader")
            else:
                self.document_loader = DocumentLoaderMarkItDown()
                self.logger.info("Using MarkItDown document loader")
            
            # Initialize extractor
            self.extractor = Extractor()
            self.extractor.load_document_loader(self.document_loader)
            
            # Configure model based on provider
            self._configure_model_provider()
            
            # Attach extractor to classifications
            for classification in self.classifications:
                classification.extractor = self.extractor
            
            # Initialize process
            self.process = Process()
            self.process.load_document_loader(self.document_loader)
            
            # Configure splitter based on model capabilities and provider
            self._configure_splitter()
            
            self.logger.info("Document intelligence components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize document intelligence components: {e}")
            raise

    def _configure_model_provider(self):
        """Configure the model provider (Ollama, Hugging Face, etc.)"""
        try:
            active_provider = model_manager.get_active_provider_name()
            
            if active_provider == "ollama":
                # Configure for Ollama
                os.environ["API_BASE"] = settings.OLLAMA_API_BASE
                model_name = f"ollama/{settings.OLLAMA_MODEL}"
                self.extractor.load_llm(model_name)
                self.logger.info(f"Using Ollama model: {settings.OLLAMA_MODEL}")
                
            elif active_provider == "huggingface":
                # Configure for Hugging Face
                # ExtractThinker supports custom LLM providers, so we'll create a wrapper
                self._setup_huggingface_extractor()
                self.logger.info(f"Using Hugging Face model: {settings.HF_MODEL_NAME}")
                
            else:
                # Fallback to OpenAI or other supported providers
                self.logger.warning(f"Unknown provider {active_provider}, using default configuration")
                model_name = f"ollama/{settings.OLLAMA_MODEL}"
                self.extractor.load_llm(model_name)
                
        except Exception as e:
            self.logger.error(f"Failed to configure model provider: {e}")
            # Fallback to Ollama
            os.environ["API_BASE"] = settings.OLLAMA_API_BASE
            model_name = f"ollama/{settings.OLLAMA_MODEL}"
            self.extractor.load_llm(model_name)

    def _setup_huggingface_extractor(self):
        """Setup extractor for Hugging Face models"""
        # For now, we'll use a custom approach since ExtractThinker may not directly support HF
        # This is a placeholder for custom HF integration
        try:
            # Check if model manager has HF provider available
            if "huggingface" not in model_manager.get_available_providers():
                raise RuntimeError("Hugging Face provider not available")
            
            # For demonstration, we'll still use Ollama API format but log HF usage
            # In a full implementation, you'd create a custom LLM wrapper for ExtractThinker
            self.logger.info("Setting up Hugging Face integration...")
            
            # Fallback to Ollama format for ExtractThinker compatibility
            os.environ["API_BASE"] = settings.OLLAMA_API_BASE
            model_name = f"ollama/{settings.OLLAMA_MODEL}"
            self.extractor.load_llm(model_name)
            
            # Note: In production, you'd implement a custom LLM provider for ExtractThinker
            self.logger.warning("Using Ollama format for ExtractThinker - HF model will be used for direct generation")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Hugging Face extractor: {e}")
            raise

    def _configure_splitter(self):
        """Configure document splitter based on model capabilities"""
        try:
            active_provider = model_manager.get_active_provider_name()
            
            if settings.MAX_CONTEXT_TOKENS <= 8192:
                # Use text splitter for limited context models
                if active_provider == "ollama":
                    model_name = f"ollama/{settings.OLLAMA_MODEL}"
                else:
                    # For HF and others, use a generic configuration
                    model_name = "text-splitter"
                
                splitter = TextSplitter(model=model_name)
                self.logger.info("Using text splitter for limited context model")
            else:
                # Use image splitter for models with larger context
                if active_provider == "ollama":
                    vision_model = f"ollama/{settings.OLLAMA_VISION_MODEL}"
                else:
                    # For HF vision models
                    vision_model = "vision-splitter"
                
                splitter = ImageSplitter(model=vision_model)
                self.logger.info("Using image splitter for vision-capable model")
            
            self.process.load_splitter(splitter)
            
        except Exception as e:
            self.logger.error(f"Failed to configure splitter: {e}")
            # Fallback to text splitter
            splitter = TextSplitter(model="text-splitter")
            self.process.load_splitter(splitter)

    def mask_pii(self, text: str) -> str:
        """Mask PII in text before processing"""
        if not settings.ENABLE_PII_MASKING or not self.analyzer:
            return text
        
        try:
            # Analyze text for PII
            results = self.analyzer.analyze(text=text, language='en')
            
            # Anonymize detected PII
            anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
            
            return anonymized_result.text
        except Exception as e:
            self.logger.warning(f"PII masking failed: {e}")
            return text

    def process_document(
        self, 
        file_path: str, 
        use_vision: bool = False,
        splitting_strategy: SplittingStrategy = SplittingStrategy.LAZY,
        completion_strategy: CompletionStrategy = CompletionStrategy.PAGINATE
    ) -> List[Contract]:
        """
        Process a document and extract structured data
        
        Args:
            file_path: Path to the document file
            use_vision: Whether to use vision-capable models
            splitting_strategy: Strategy for splitting documents (LAZY for limited context)
            completion_strategy: Strategy for handling responses (PAGINATE for limited context)
        
        Returns:
            List of extracted contract objects
        """
        try:
            self.logger.info(f"Processing document: {file_path}")
            
            # Ensure directories exist
            os.makedirs(settings.DOCUMENT_UPLOAD_PATH, exist_ok=True)
            os.makedirs(settings.EXTRACTED_DATA_PATH, exist_ok=True)
            
            # Process the document
            result = (
                self.process
                .load_file(file_path)
                .split(self.classifications, strategy=splitting_strategy)
                .extract(vision=use_vision, completion_strategy=completion_strategy)
            )
            
            # Log results
            self.logger.info(f"Extracted {len(result)} items from document")
            for item in result:
                self.logger.info(f"Extracted {type(item).__name__}: {item}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            raise

    def classify_document(self, file_path: str) -> Optional[str]:
        """Classify a document type"""
        try:
            # Load and analyze the document for classification
            with open(file_path, 'rb') as file:
                # This is a simplified classification - in practice you'd use the model
                # to analyze the document content and determine its type
                content = file.read()
                
                # For demo purposes, classify based on file name patterns
                file_name = Path(file_path).name.lower()
                
                if 'invoice' in file_name or 'bill' in file_name:
                    return "Invoice"
                elif 'license' in file_name or 'dl' in file_name:
                    return "Driver License"
                elif 'passport' in file_name:
                    return "Passport"
                elif 'business' in file_name or 'card' in file_name:
                    return "Business Card"
                else:
                    return "Unknown"
                    
        except Exception as e:
            self.logger.error(f"Document classification failed: {e}")
            return None

    def extract_with_pagination(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract data using pagination for models with limited context windows
        """
        try:
            self.logger.info(f"Extracting with pagination: {file_path}")
            
            # Use paginated completion strategy for limited context models
            result = self.process_document(
                file_path=file_path,
                use_vision=False,
                splitting_strategy=SplittingStrategy.LAZY,
                completion_strategy=CompletionStrategy.PAGINATE
            )
            
            # Convert to dictionaries for easier handling
            extracted_data = []
            for item in result:
                if hasattr(item, 'dict'):
                    extracted_data.append(item.dict())
                else:
                    extracted_data.append(str(item))
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Paginated extraction failed: {e}")
            raise

    def batch_process_documents(self, document_paths: List[str]) -> Dict[str, List[Contract]]:
        """Process multiple documents in batch"""
        results = {}
        
        for doc_path in document_paths:
            try:
                self.logger.info(f"Processing document in batch: {doc_path}")
                result = self.process_document(doc_path)
                results[doc_path] = result
            except Exception as e:
                self.logger.error(f"Failed to process {doc_path}: {e}")
                results[doc_path] = []
        
        return results

    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".docx", ".doc", ".txt"]

    def validate_document(self, file_path: str) -> bool:
        """Validate if document format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.get_supported_formats()
    
    def generate_with_model(self, prompt: str, **kwargs) -> str:
        """Generate text using the current model provider"""
        try:
            return model_manager.generate(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Model generation failed: {e}")
            raise

    def switch_model_provider(self, provider_name: str) -> bool:
        """Switch to a different model provider"""
        try:
            success = model_manager.switch_provider(provider_name)
            if success:
                # Reconfigure extractor for new provider
                self._configure_model_provider()
                self._configure_splitter()
                self.logger.info(f"Switched to model provider: {provider_name}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to switch model provider: {e}")
            return False

    def get_available_providers(self) -> List[str]:
        """Get list of available model providers"""
        return model_manager.get_available_providers()

    def get_current_provider_info(self) -> Dict[str, Any]:
        """Get information about current model provider"""
        active_provider = model_manager.get_active_provider_name()
        if active_provider:
            return model_manager.get_provider_info(active_provider)
        return {"status": "no_active_provider"}

    def get_all_provider_info(self) -> Dict[str, Any]:
        """Get information about all available providers"""
        return model_manager.get_provider_info()

    def process_document_with_provider(
        self, 
        file_path: str,
        provider_name: str = None,
        use_vision: bool = False,
        splitting_strategy: SplittingStrategy = SplittingStrategy.LAZY,
        completion_strategy: CompletionStrategy = CompletionStrategy.PAGINATE
    ) -> List[Contract]:
        """
        Process document with specific provider
        
        Args:
            file_path: Path to the document file
            provider_name: Specific provider to use (ollama, huggingface)
            use_vision: Whether to use vision-capable models
            splitting_strategy: Strategy for splitting documents
            completion_strategy: Strategy for handling responses
        
        Returns:
            List of extracted contract objects
        """
        original_provider = model_manager.get_active_provider_name()
        
        try:
            # Switch to requested provider if specified
            if provider_name and provider_name != original_provider:
                if not self.switch_model_provider(provider_name):
                    raise ValueError(f"Cannot switch to provider: {provider_name}")
            
            # Process document
            result = self.process_document(
                file_path=file_path,
                use_vision=use_vision,
                splitting_strategy=splitting_strategy,
                completion_strategy=completion_strategy
            )
            
            return result
            
        finally:
            # Restore original provider if we switched
            if provider_name and provider_name != original_provider and original_provider:
                self.switch_model_provider(original_provider)

    def benchmark_providers(self, test_prompt: str) -> Dict[str, Dict[str, Any]]:
        """
        Benchmark different providers with a test prompt
        
        Args:
            test_prompt: Test prompt to use for benchmarking
            
        Returns:
            Dictionary with performance metrics for each provider
        """
        results = {}
        original_provider = model_manager.get_active_provider_name()
        
        for provider_name in self.get_available_providers():
            try:
                import time
                
                # Switch to provider
                if not self.switch_model_provider(provider_name):
                    results[provider_name] = {"status": "failed_to_switch"}
                    continue
                
                # Measure generation time
                start_time = time.time()
                response = self.generate_with_model(test_prompt, max_tokens=100)
                end_time = time.time()
                
                results[provider_name] = {
                    "status": "success",
                    "response_length": len(response),
                    "generation_time": end_time - start_time,
                    "provider_info": self.get_current_provider_info()
                }
                
            except Exception as e:
                results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Restore original provider
        if original_provider:
            self.switch_model_provider(original_provider)
        
        return results
