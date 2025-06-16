"""
Enhanced Document Intelligence Example with Ollama and Hugging Face Models

This example demonstrates how to use both local Ollama models and Hugging Face models
for document intelligence, with automatic fallback and provider switching.
"""
import asyncio
import os
import logging
from pathlib import Path
import time

from src.workflows.document_intelligence_workflow import (
    DocumentIntelligenceWorkflow,
    process_document_with_local_llm
)
from src.agents.document_intelligence_agent import DocumentIntelligenceAgent
from src.utils.model_manager import model_manager
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_provider_status():
    """Display status of all model providers"""
    print("\n=== Model Provider Status ===")
    
    available_providers = model_manager.get_available_providers()
    active_provider = model_manager.get_active_provider_name()
    
    print(f"Available Providers: {', '.join(available_providers) if available_providers else 'None'}")
    print(f"Active Provider: {active_provider or 'None'}")
    
    # Get detailed info for each provider
    all_info = model_manager.get_provider_info()
    for provider, info in all_info.items():
        print(f"\n{provider.upper()} Provider:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    print("=" * 50)

def setup_environment():
    """Setup instructions for both Ollama and Hugging Face"""
    print("=== Multi-Provider Setup Instructions ===")
    print("\n1. Ollama Setup:")
    print("   - Install Ollama: https://ollama.ai/")
    print("   - Pull models: ollama pull phi4 && ollama pull moondream")
    print("   - Start service: ollama serve")
    
    print("\n2. Hugging Face Setup:")
    print("   - Get HF token: https://huggingface.co/settings/tokens")
    print("   - Set HF_TOKEN environment variable")
    print("   - Ensure sufficient GPU memory (8GB+ recommended)")
    print("   - Models will auto-download on first use")
    
    print("\n3. Configuration:")
    print(f"   - Primary provider: {settings.MODEL_PROVIDER}")
    print(f"   - Fallback provider: {settings.FALLBACK_PROVIDER}")
    print(f"   - HF model: {settings.HF_MODEL_NAME}")
    print(f"   - Ollama model: {settings.OLLAMA_MODEL}")
    print("=" * 50)

def create_enhanced_sample_documents():
    """Create more comprehensive sample documents for testing"""
    documents_dir = Path("./sample_documents")
    documents_dir.mkdir(exist_ok=True)
    
    # Complex invoice with more fields
    complex_invoice = """
    INVOICE #INV-2025-0001
    Date: June 16, 2025
    Due Date: July 16, 2025
    
    BILL TO:                           SHIP TO:
    TechCorp Solutions                 TechCorp Solutions - East Campus
    Attn: John Doe                     Attn: Jane Smith
    123 Main Street, Suite 400         456 Innovation Drive
    Anytown, ST 12345                  Tech City, ST 67890
    Phone: (555) 123-4567             Phone: (555) 987-6543
    Email: accounts@techcorp.com       Email: receiving@techcorp.com
    
    FROM:
    AI Solutions Inc.
    789 Future Lane
    Innovation Valley, CA 90210
    Tax ID: 12-3456789
    
    DESCRIPTION                      QTY    RATE        AMOUNT
    ────────────────────────────────────────────────────────
    AI Consulting Services          40     $150.00     $6,000.00
    Document Intelligence Setup     8      $200.00     $1,600.00
    Model Training & Optimization   16     $175.00     $2,800.00
    Technical Support (3 months)    1      $500.00     $500.00
    
                                           SUBTOTAL:    $10,900.00
                                           TAX (8.5%):  $926.50
                                           SHIPPING:    $100.00
                                           ──────────────────
                                           TOTAL:       $11,926.50
    
    Payment Terms: Net 30
    Payment Methods: Check, Wire Transfer, ACH
    
    Thank you for your business!
    """
    
    invoice_path = documents_dir / "complex_invoice.txt"
    with open(invoice_path, 'w') as f:
        f.write(complex_invoice)
    
    # Driver license document
    driver_license = """
    DEPARTMENT OF MOTOR VEHICLES
    
    DRIVER LICENSE
    
    License Number: D123456789
    Class: C - Regular Driver License
    
    PERSONAL INFORMATION:
    Name: Sarah Johnson
    Date of Birth: March 15, 1985
    Age: 40
    Sex: F
    Height: 5'6"
    Weight: 140 lbs
    Eye Color: Brown
    Hair Color: Black
    
    ADDRESS:
    123 Oak Street
    Springfield, IL 62704
    
    RESTRICTIONS: None
    ENDORSEMENTS: None
    
    Issue Date: June 16, 2020
    Expiration Date: June 16, 2025
    
    FOR RENEWAL VISIT: www.dmv.state.il.us
    """
    
    license_path = documents_dir / "driver_license.txt"
    with open(license_path, 'w') as f:
        f.write(driver_license)
    
    # Professional business card
    business_card = """
    ╔══════════════════════════════════════╗
    ║           TECHSOLUTIONS              ║
    ║              AI DIVISION             ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║    Dr. Michael Rodriguez             ║
    ║    Senior AI Research Scientist      ║
    ║                                      ║
    ║    📧 m.rodriguez@techsolutions.ai   ║
    ║    📱 +1 (555) 234-5678             ║
    ║    🌐 linkedin.com/in/mrodriguez-ai  ║
    ║                                      ║
    ║    📍 2001 Tech Park Drive           ║
    ║       Silicon Valley, CA 94025      ║
    ║                                      ║
    ║    "Innovating the Future with AI"   ║
    ╚══════════════════════════════════════╝
    """
    
    business_card_path = documents_dir / "business_card.txt"
    with open(business_card_path, 'w') as f:
        f.write(business_card)
    
    return [str(invoice_path), str(license_path), str(business_card_path)]

def demonstrate_provider_switching():
    """Demonstrate switching between different model providers"""
    print("\n=== Provider Switching Demo ===")
    
    try:
        agent = DocumentIntelligenceAgent()
        
        # Show available providers
        providers = agent.get_available_providers()
        print(f"Available providers: {providers}")
        
        if len(providers) < 2:
            print("Need at least 2 providers for switching demo")
            return
        
        # Test prompt
        test_prompt = "Extract the following information from this text: Name: John Doe, Age: 30, Email: john@example.com"
        
        # Benchmark providers
        print("\nBenchmarking providers...")
        benchmark_results = agent.benchmark_providers(test_prompt)
        
        for provider, result in benchmark_results.items():
            print(f"\n{provider.upper()} Results:")
            if result.get('status') == 'success':
                print(f"  Generation time: {result['generation_time']:.2f}s")
                print(f"  Response length: {result['response_length']} chars")
            else:
                print(f"  Status: {result.get('status', 'unknown')}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
        
    except Exception as e:
        print(f"Provider switching demo failed: {e}")

def demonstrate_document_processing_with_providers():
    """Demonstrate document processing with different providers"""
    print("\n=== Multi-Provider Document Processing Demo ===")
    
    # Create sample documents
    sample_docs = create_enhanced_sample_documents()
    
    try:
        agent = DocumentIntelligenceAgent()
        available_providers = agent.get_available_providers()
        
        if not available_providers:
            print("No model providers available")
            return
        
        # Process the same document with different providers
        test_doc = sample_docs[0]  # Complex invoice
        print(f"Processing: {Path(test_doc).name}")
        
        results = {}
        
        for provider in available_providers:
            print(f"\n--- Processing with {provider.upper()} ---")
            try:
                start_time = time.time()
                
                result = agent.process_document_with_provider(
                    file_path=test_doc,
                    provider_name=provider,
                    use_vision=False
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                results[provider] = {
                    'success': True,
                    'processing_time': processing_time,
                    'extracted_items': len(result),
                    'data': result
                }
                
                print(f"✓ Success - {len(result)} items extracted in {processing_time:.2f}s")
                
                # Show first extracted item as example
                if result:
                    first_item = result[0]
                    if hasattr(first_item, 'dict'):
                        item_dict = first_item.dict()
                        print(f"Sample extracted data: {list(item_dict.keys())[:3]}...")
                
            except Exception as e:
                results[provider] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"✗ Failed: {e}")
        
        # Compare results
        print(f"\n--- Processing Comparison ---")
        for provider, result in results.items():
            if result['success']:
                print(f"{provider}: {result['extracted_items']} items, {result['processing_time']:.2f}s")
            else:
                print(f"{provider}: Failed - {result['error']}")
        
    except Exception as e:
        print(f"Multi-provider processing demo failed: {e}")

def demonstrate_fallback_behavior():
    """Demonstrate automatic fallback between providers"""
    print("\n=== Fallback Behavior Demo ===")
    
    try:
        # Create a sample document
        sample_docs = create_enhanced_sample_documents()
        test_doc = sample_docs[1]  # Driver license
        
        print(f"Processing document with automatic fallback: {Path(test_doc).name}")
        
        # Use the workflow which should handle fallback automatically
        result = process_document_with_local_llm(
            document_path=test_doc,
            use_vision=False,
            enable_pii_masking=True
        )
        
        print(f"Result status: {result['status']}")
        print(f"Document type: {result['document_type']}")
        print(f"Extracted items: {len(result['extracted_data'])}")
        
        if result['extracted_data']:
            print("Sample extracted data:")
            for item in result['extracted_data'][:2]:  # Show first 2 items
                print(f"  - {item}")
        
        if result['error_message']:
            print(f"Errors encountered: {result['error_message']}")
        
    except Exception as e:
        print(f"Fallback demo failed: {e}")

def demonstrate_provider_comparison():
    """Compare capabilities of different providers"""
    print("\n=== Provider Capability Comparison ===")
    
    try:
        # Get provider information
        all_info = model_manager.get_provider_info()
        
        comparison_table = []
        headers = ["Provider", "Status", "Model", "Device", "Quantized"]
        
        for provider, info in all_info.items():
            row = [
                provider.upper(),
                info.get('status', 'unknown'),
                info.get('name', 'unknown'),
                info.get('device', 'unknown'),
                str(info.get('quantized', 'N/A'))
            ]
            comparison_table.append(row)
        
        # Print comparison table
        print(f"\n{'Provider':<12} {'Status':<12} {'Model':<20} {'Device':<10} {'Quantized':<10}")
        print("-" * 70)
        
        for row in comparison_table:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<20} {row[3]:<10} {row[4]:<10}")
        
        # Performance characteristics
        print(f"\n=== Performance Characteristics ===")
        print("Ollama:")
        print("  + Easy setup and management")
        print("  + Optimized for local inference")
        print("  + Lower memory usage")
        print("  - May have slightly lower quality")
        
        print("\nHugging Face:")
        print("  + Latest model versions")
        print("  + Higher quality outputs")
        print("  + Fine-tuning capabilities")
        print("  - Higher memory requirements")
        print("  - More complex setup")
        
    except Exception as e:
        print(f"Provider comparison failed: {e}")

def recommend_provider_setup():
    """Provide recommendations for provider setup"""
    print("\n=== Provider Setup Recommendations ===")
    
    print("Choose your setup based on your requirements:")
    print("\n1. Privacy-First & Simple Setup:")
    print("   Primary: Ollama")
    print("   Fallback: None")
    print("   Benefits: Easy setup, no cloud dependencies")
    
    print("\n2. Best Quality & Performance:")
    print("   Primary: Hugging Face")
    print("   Fallback: Ollama")
    print("   Benefits: Latest models, high quality, local fallback")
    
    print("\n3. Production & Reliability:")
    print("   Primary: Ollama")
    print("   Fallback: Hugging Face")
    print("   Benefits: Stable local processing, HF for complex cases")
    
    print("\n4. Development & Testing:")
    print("   Primary: Hugging Face")
    print("   Fallback: OpenAI (if available)")
    print("   Benefits: Fast iteration, cloud fallback")
    
    # Current setup
    print(f"\nYour current setup:")
    print(f"  Primary: {settings.MODEL_PROVIDER}")
    print(f"  Fallback: {settings.FALLBACK_PROVIDER}")
    
    available = model_manager.get_available_providers()
    print(f"  Available: {', '.join(available) if available else 'None'}")

def main():
    """Main demonstration function"""
    print("Enhanced Document Intelligence with Multiple Model Providers")
    print("=" * 60)
    
    # Setup instructions
    setup_environment()
    
    # Display provider status
    display_provider_status()
    
    # Check if any providers are available
    available_providers = model_manager.get_available_providers()
    if not available_providers:
        print("\n❌ No model providers available!")
        print("Please set up at least one provider (Ollama or Hugging Face)")
        recommend_provider_setup()
        return
    
    print(f"\n✅ Found {len(available_providers)} available provider(s)")
    
    # Run demonstrations
    try:
        demonstrate_provider_comparison()
        demonstrate_provider_switching()
        demonstrate_document_processing_with_providers()
        demonstrate_fallback_behavior()
        recommend_provider_setup()
        
        print("\n=== Demo Complete ===")
        print("Next steps:")
        print("1. Experiment with different models and providers")
        print("2. Try your own documents")
        print("3. Configure provider priorities for your use case")
        print("4. Set up both providers for maximum reliability")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nDemo failed: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    main()
