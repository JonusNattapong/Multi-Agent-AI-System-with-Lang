"""
Business Document Analysis Demo

This example demonstrates the specialized BusinessDocumentProcessor
using real business documents from your workspace.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.business_document_processor import (
    BusinessDocumentProcessor,
    analyze_business_documents
)

def main():
    """Demonstrate business document analysis with real data"""
    print("🏢 Business Document Analysis Demo")
    print("=" * 60)
    
    # Define real document paths from your workspace
    document_paths = [
        "documents/reports/quarterly_business_review_q4_2024.txt",
        "documents/reports/ai_system_performance_report_2024.txt",
        "documents/policies/data_privacy_security_policy.txt",
        "documents/specifications/document_intelligence_api_spec.txt"
    ]
    
    # Filter to existing documents
    existing_docs = []
    for doc_path in document_paths:
        if os.path.exists(doc_path):
            existing_docs.append(doc_path)
            print(f"✓ Found: {doc_path}")
        else:
            print(f"✗ Missing: {doc_path}")
    
    if not existing_docs:
        print("\n❌ No business documents found!")
        print("Please ensure you have documents in the documents/ folder")
        return
    
    print(f"\n🔍 Analyzing {len(existing_docs)} business documents...")
    print("-" * 40)
    
    # Use the convenience function for quick analysis
    results = analyze_business_documents(existing_docs)
    
    # Display results
    print("\n📊 ANALYSIS RESULTS")
    print("=" * 40)
    
    # Financial Summary
    financial = results.get('financial_summary', {})
    if financial:
        print("\n💰 FINANCIAL METRICS:")
        for key, value in financial.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Performance Summary  
    performance = results.get('performance_summary', {})
    if performance:
        print("\n⚡ PERFORMANCE METRICS:")
        for key, value in performance.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Compliance Summary
    compliance = results.get('compliance_summary', {})
    if compliance:
        print("\n🔒 COMPLIANCE STATUS:")
        if compliance.get('standards'):
            print(f"  • Standards: {', '.join(set(compliance['standards']))}")
    
    # Business Insights
    insights = results.get('business_insights', [])
    if insights:
        print("\n🎯 KEY INSIGHTS:")
        for insight in insights:
            print(f"  • {insight}")
    
    # Document Processing Summary
    processed = results.get('documents_processed', [])
    print(f"\n📋 PROCESSING SUMMARY:")
    print(f"  • Documents analyzed: {len(processed)}")
    
    successful = sum(1 for doc in processed if 'error' not in doc)
    print(f"  • Successfully processed: {successful}/{len(processed)}")
    
    # Generate Executive Summary
    print("\n📄 Generating Executive Summary...")
    processor = BusinessDocumentProcessor()
    executive_summary = processor.generate_executive_summary(results)
    
    print(executive_summary)
    
    # Save results to file
    output_dir = Path("extracted")
    output_dir.mkdir(exist_ok=True)
    
    # Save detailed results as JSON
    import json
    results_file = output_dir / "business_analysis_results.json"
    
    # Convert results to JSON-serializable format
    json_results = {}
    for key, value in results.items():
        try:
            json.dumps(value)  # Test if serializable
            json_results[key] = value
        except TypeError:
            # Convert non-serializable objects to string
            json_results[key] = str(value)
    
    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    # Save executive summary
    summary_file = output_dir / "executive_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(executive_summary)
    
    print(f"\n💾 Results saved:")
    print(f"  • Detailed data: {results_file}")
    print(f"  • Executive summary: {summary_file}")
    
    print(f"\n✅ Business document analysis complete!")

if __name__ == "__main__":
    main()
