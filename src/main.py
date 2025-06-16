#!/usr/bin/env python3
"""
Multi-Agent AI System using LangGraph and LangSmith
Main entry point for the application
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from config import settings
from utils import setup_logging, get_logger
from workflows.content_creation import ContentCreationWorkflow
from workflows.research_workflow import ResearchWorkflow

# Setup logging
logger = setup_logging()

def demo_content_creation():
    """Demonstrate the content creation workflow"""
    logger.info("=== Content Creation Workflow Demo ===")
    
    workflow = ContentCreationWorkflow()
    
    # Run content creation for an AI article
    result = workflow.run(
        "Write a comprehensive article about the future of artificial intelligence in 2024",
        initial_context={
            "target_audience": "technology professionals",
            "article_length": "1500-2000 words",
            "tone": "professional but engaging"
        }
    )
    
    if result["success"]:
        print("\n🎉 Content Creation Completed Successfully!")
        print(f"\n📄 Final Content Preview:\n{result['final_content'][:500]}...\n")
        print(f"📝 Review Feedback:\n{result['review_feedback'][:300]}...\n")
    else:
        print(f"❌ Content creation failed: {result.get('error', 'Unknown error')}")
    
    return result

def demo_research_workflow():
    """Demonstrate the research workflow"""
    logger.info("=== Research Workflow Demo ===")
    
    workflow = ResearchWorkflow()
    
    # Run comprehensive research
    result = workflow.run(
        "Multi-agent systems in artificial intelligence: current trends and future applications"
    )
    
    if result["success"]:
        print("\n🔬 Research Completed Successfully!")
        print(f"\n📊 Research Synopsis:\n{result['synthesis'][:400]}...\n")
        print(f"✅ Validation Results:\n{result['validation'][:300]}...\n")
    else:
        print(f"❌ Research failed: {result.get('error', 'Unknown error')}")
    
    return result

def demo_collaborative_research():
    """Demonstrate collaborative research across multiple topics"""
    logger.info("=== Collaborative Research Demo ===")
    
    workflow = ResearchWorkflow()
    
    topics = [
        "LangGraph framework capabilities and use cases",
        "LangSmith monitoring and debugging features", 
        "Multi-agent coordination patterns and best practices"
    ]
    
    result = workflow.run_collaborative_research(topics)
    
    if result["success"]:
        print("\n🤝 Collaborative Research Completed!")
        print(f"\n🔄 Topics Researched: {len(result['research_topics'])}")
        print(f"\n🎯 Collaborative Synthesis:\n{result['collaborative_synthesis'][:400]}...\n")
    else:
        print("❌ Collaborative research failed")
    
    return result

def interactive_mode():
    """Run in interactive mode allowing user to choose demos"""
    print("\n🤖 Multi-Agent AI System Demo")
    print("=" * 40)
    
    while True:
        print("\nChoose a demo:")
        print("1. Content Creation Workflow")
        print("2. Research Workflow") 
        print("3. Collaborative Research")
        print("4. Run All Demos")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demo_content_creation()
        elif choice == "2":
            demo_research_workflow()
        elif choice == "3":
            demo_collaborative_research()
        elif choice == "4":
            print("\n🚀 Running All Demos...")
            demo_content_creation()
            demo_research_workflow()
            demo_collaborative_research()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main application entry point"""
    logger.info("Starting Multi-Agent AI System")
    
    # Validate configuration
    if not settings.validate_config():
        logger.error("Configuration validation failed. Please check your environment variables.")
        sys.exit(1)
    
    print("🚀 Multi-Agent AI System with LangGraph and LangSmith")
    print(f"📊 LangSmith Tracing: {'Enabled' if settings.LANGCHAIN_TRACING_V2 else 'Disabled'}")
    print(f"🔧 Debug Mode: {'Enabled' if settings.DEBUG else 'Disabled'}")
    
    # Check if running in demo mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "content":
            demo_content_creation()
        elif mode == "research":
            demo_research_workflow()
        elif mode == "collaborative":
            demo_collaborative_research()
        elif mode == "all":
            demo_content_creation()
            demo_research_workflow()  
            demo_collaborative_research()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: content, research, collaborative, all")
    else:
        # Run in interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
