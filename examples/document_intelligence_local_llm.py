"""
Document Intelligence Example with Local LLMs (Ollama + Phi-4)

This example demonstrates how to use the document intelligence workflow
with local models for privacy-preserving document processing.
"""
import asyncio
import os
import logging
from pathlib import Path

from src.workflows.document_intelligence_workflow import (
    DocumentIntelligenceWorkflow,
    process_document_with_local_llm
)
from src.agents.document_intelligence_agent import DocumentIntelligenceAgent
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ollama_environment():
    """
    Setup instructions for Ollama with Phi-4
    """
    print("=== Ollama Setup Instructions ===")
    print("1. Install Ollama: https://ollama.ai/")
    print("2. Pull Phi-4 model: ollama pull phi4")
    print("3. Pull Moondream for vision: ollama pull moondream")
    print("4. Start Ollama service: ollama serve")
    print("5. Verify models: ollama list")
    print("=" * 50)

def create_sample_documents():
    """Create sample documents for testing"""
    documents_dir = Path("./sample_documents")
    documents_dir.mkdir(exist_ok=True)
    
    # Create a sample invoice text file
    invoice_content = """
    INVOICE #INV-2024-001
    Date: 2024-06-16
    
    Bill To:
    John Doe
    123 Main Street
    Anytown, ST 12345
    
    From:
    ABC Company
    456 Business Ave
    Business City, ST 67890
    
    Description                Quantity    Price    Total
    Consulting Services        10 hours    $150     $1,500.00
    Software License           1           $500     $500.00
    
    Subtotal: $2,000.00
    Tax: $200.00
    Total: $2,200.00
    """
    
    invoice_path = documents_dir / "sample_invoice.txt"
    with open(invoice_path, 'w') as f:
        f.write(invoice_content)
    
    # Create a sample business card text file
    business_card_content = """
    BUSINESS CARD
    
    Jane Smith
    Senior Software Engineer
    Tech Solutions Inc.
    
    Email: jane.smith@techsolutions.com
    Phone: (555) 123-4567
    Address: 789 Tech Park Drive, Innovation City, CA 90210
    """
    
    business_card_path = documents_dir / "sample_business_card.txt"
    with open(business_card_path, 'w') as f:
        f.write(business_card_content)
    
    return [str(invoice_path), str(business_card_path)]

def demonstrate_single_document_processing():
    """Demonstrate processing a single document"""
    print("\n=== Single Document Processing Demo ===")
    
    # Create sample documents
    sample_docs = create_sample_documents()
    
    # Process the first document
    document_path = sample_docs[0]
    print(f"Processing: {document_path}")
    
    try:
        # Use the convenience function
        result = process_document_with_local_llm(
            document_path=document_path,
            use_vision=False,  # Text-only processing
            enable_pii_masking=True
        )
        
        print(f"Status: {result['status']}")
        print(f"Document Type: {result['document_type']}")
        print(f"Extracted Data Items: {len(result['extracted_data'])}")
        
        for i, data in enumerate(result['extracted_data']):
            print(f"  Item {i+1}: {data}")
        
        if result['error_message']:
            print(f"Error: {result['error_message']}")
            
    except Exception as e:
        print(f"Processing failed: {e}")

def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple documents"""
    print("\n=== Batch Document Processing Demo ===")
    
    # Create sample documents
    sample_docs = create_sample_documents()
    
    try:
        workflow = DocumentIntelligenceWorkflow()
        
        # Process all documents
        results = workflow.batch_process_documents(
            document_paths=sample_docs,
            use_vision=False,
            enable_pii_masking=True
        )
        
        print(f"Processed {len(results)} documents:")
        
        for doc_path, result in results.items():
            print(f"\n--- {Path(doc_path).name} ---")
            print(f"Status: {result['status']}")
            print(f"Type: {result['document_type']}")
            print(f"Data Items: {len(result['extracted_data'])}")
            
            if result['error_message']:
                print(f"Error: {result['error_message']}")
                
    except Exception as e:
        print(f"Batch processing failed: {e}")

def demonstrate_agent_features():
    """Demonstrate direct agent features"""
    print("\n=== Document Intelligence Agent Features Demo ===")
    
    try:
        agent = DocumentIntelligenceAgent()
        
        # Show supported formats
        formats = agent.get_supported_formats()
        print(f"Supported formats: {', '.join(formats)}")
        
        # Create a sample document
        sample_docs = create_sample_documents()
        test_doc = sample_docs[0]
        
        # Validate document
        is_valid = agent.validate_document(test_doc)
        print(f"Document validation for {Path(test_doc).name}: {is_valid}")
        
        # Classify document
        doc_type = agent.classify_document(test_doc)
        print(f"Document classification: {doc_type}")
        
        # Process with pagination (for limited context models)
        if settings.MAX_CONTEXT_TOKENS <= 8192:
            print("Using pagination for limited context model...")
            paginated_result = agent.extract_with_pagination(test_doc)
            print(f"Paginated extraction result: {len(paginated_result)} items")
        
    except Exception as e:
        print(f"Agent demo failed: {e}")

def demonstrate_privacy_features():
    """Demonstrate PII masking and privacy features"""
    print("\n=== Privacy and PII Masking Demo ===")
    
    try:
        agent = DocumentIntelligenceAgent()
        
        # Sample text with PII
        sample_text = """
        Name: John Doe
        Email: john.doe@email.com
        Phone: (555) 123-4567
        SSN: 123-45-6789
        Credit Card: 4532-1234-5678-9012
        """
        
        print("Original text:")
        print(sample_text)
        
        # Mask PII
        masked_text = agent.mask_pii(sample_text)
        print("\nMasked text:")
        print(masked_text)
        
    except Exception as e:
        print(f"PII masking demo failed: {e}")

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    import requests
    
    try:
        response = requests.get(f"{settings.OLLAMA_API_BASE}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running. Available models: {len(models)}")
            
            # Check for required models
            model_names = [model['name'] for model in models]
            phi4_available = any('phi4' in name for name in model_names)
            moondream_available = any('moondream' in name for name in model_names)
            
            print(f"  Phi-4 available: {phi4_available}")
            print(f"  Moondream available: {moondream_available}")
            
            if not phi4_available:
                print("  Warning: Phi-4 model not found. Run: ollama pull phi4")
            
            return True
        else:
            print(f"✗ Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is installed and running: ollama serve")
        return False

def main():
    """Main demonstration function"""
    print("Document Intelligence with Local LLMs Demo")
    print("=" * 50)
    
    # Show setup instructions
    setup_ollama_environment()
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("\nSkipping demos due to Ollama connection issues.")
        print("Please ensure Ollama is installed and running.")
        return
    
    # Show configuration
    print(f"\nCurrent Configuration:")
    print(f"  Ollama API Base: {settings.OLLAMA_API_BASE}")
    print(f"  Model: {settings.OLLAMA_MODEL}")
    print(f"  Vision Model: {settings.OLLAMA_VISION_MODEL}")
    print(f"  Max Context Tokens: {settings.MAX_CONTEXT_TOKENS}")
    print(f"  PII Masking: {settings.ENABLE_PII_MASKING}")
    print(f"  Document Loader: {settings.DOC_LOADER_TYPE}")
    
    # Run demonstrations
    try:
        demonstrate_agent_features()
        demonstrate_privacy_features()
        demonstrate_single_document_processing()
        demonstrate_batch_processing()
        
        print("\n=== Demo Complete ===")
        print("Next steps:")
        print("1. Try with your own PDF files")
        print("2. Experiment with different models (llama3.3, qwen2.5)")
        print("3. Enable vision models for complex layouts")
        print("4. Scale up with larger context windows")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nDemo failed: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    main()
