#!/usr/bin/env python3
"""
Content Creation Pipeline Example
Demonstrates the full content creation workflow with feedback loops
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from workflows.content_creation import ContentCreationWorkflow
from utils import get_logger
from tools import SaveContentTool

logger = get_logger("examples.content_pipeline")

def blog_post_creation():
    """Create a blog post using the content creation pipeline"""
    logger.info("Creating blog post with content pipeline")
    
    workflow = ContentCreationWorkflow()
    
    task = "Write an engaging blog post about the benefits of remote work"
    context = {
        "target_audience": "professionals considering remote work",
        "tone": "friendly and informative",
        "length": "800-1200 words",
        "include_sections": ["Introduction", "Benefits", "Challenges", "Tips", "Conclusion"]
    }
    
    print("📝 Starting blog post creation...")
    result = workflow.run(task, context)
    
    if result["success"]:
        print("✅ Blog post created successfully!")
        
        # Save the content
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            result["final_content"], 
            "remote_work_blog_post", 
            "md"
        )
        print(f"💾 {save_result}")
        
        print(f"\n📊 Content Stats:")
        print(f"- Length: {len(result['final_content'])} characters")
        print(f"- Research completed: ✅")
        print(f"- Writing completed: ✅") 
        print(f"- Review completed: ✅")
        
        return result
    else:
        print(f"❌ Blog post creation failed: {result.get('error', 'Unknown error')}")
        return None

def technical_documentation():
    """Create technical documentation"""
    logger.info("Creating technical documentation")
    
    workflow = ContentCreationWorkflow()
    
    task = "Create technical documentation for a REST API"
    context = {
        "target_audience": "developers",
        "format": "technical documentation", 
        "include_examples": True,
        "sections": ["Overview", "Authentication", "Endpoints", "Examples", "Error Codes"]
    }
    
    print("📚 Starting technical documentation creation...")
    result = workflow.run(task, context)
    
    if result["success"]:
        print("✅ Technical documentation created!")
        
        # Save as markdown
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            result["final_content"],
            "api_documentation",
            "md" 
        )
        print(f"💾 {save_result}")
        
        return result
    else:
        print(f"❌ Documentation creation failed: {result.get('error', 'Unknown error')}")
        return None

def iterative_content_improvement():
    """Demonstrate iterative content improvement"""
    logger.info("Starting iterative content improvement")
    
    workflow = ContentCreationWorkflow()
    
    task = "Write a product description for a smart home device"
    
    print("🔄 Starting iterative content creation...")
    result = workflow.run_with_feedback_loop(task, max_iterations=3)
    
    if result["success"]:
        print(f"✅ Content improved over {result['iterations']} iterations!")
        
        # Save final version
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            result["final_content"],
            "smart_home_product_description",
            "txt"
        )
        print(f"💾 {save_result}")
        
        return result
    else:
        print("❌ Iterative improvement failed")
        return None

def marketing_content_suite():
    """Create a suite of marketing content"""
    logger.info("Creating marketing content suite")
    
    workflow = ContentCreationWorkflow()
    
    base_product = "EcoSmart Solar Panel System"
    
    content_types = [
        ("Product Landing Page", {
            "target_audience": "homeowners",
            "tone": "persuasive and informative",
            "focus": "benefits and features"
        }),
        ("Email Campaign", {
            "target_audience": "potential customers", 
            "tone": "friendly and urgent",
            "focus": "limited time offer"
        }),
        ("Social Media Post", {
            "target_audience": "general public",
            "tone": "engaging and shareable", 
            "focus": "environmental benefits"
        })
    ]
    
    results = {}
    
    for content_type, context in content_types:
        print(f"\n📄 Creating {content_type}...")
        
        task = f"Create {content_type.lower()} content for {base_product}"
        context["content_type"] = content_type
        
        result = workflow.run(task, context)
        
        if result["success"]:
            print(f"✅ {content_type} created!")
            results[content_type] = result
            
            # Save each piece
            save_tool = SaveContentTool()
            filename = f"{base_product}_{content_type}".lower().replace(" ", "_")
            save_result = save_tool._run(result["final_content"], filename, "md")
            print(f"💾 Saved as {filename}.md")
        else:
            print(f"❌ {content_type} creation failed")
            results[content_type] = None
    
    return results

def main():
    """Run content creation pipeline examples"""
    print("📝 Content Creation Pipeline Examples")
    print("=" * 45)
    
    examples = [
        ("Blog Post Creation", blog_post_creation),
        ("Technical Documentation", technical_documentation),
        ("Iterative Content Improvement", iterative_content_improvement),
        ("Marketing Content Suite", marketing_content_suite)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        print("-" * 35)
        
        try:
            result = func()
            print("✅ Example completed successfully!")
        except Exception as e:
            logger.error(f"Example failed: {str(e)}")
            print(f"❌ Example failed: {str(e)}")
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")

if __name__ == "__main__":
    main()
