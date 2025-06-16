#!/usr/bin/env python3
"""
Research Analysis Example
Demonstrates advanced research workflows and analysis capabilities
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from workflows.research_workflow import ResearchWorkflow
from agents import ResearchAgent
from tools import SaveContentTool
from utils import get_logger

logger = get_logger("examples.research_analysis")

def comprehensive_market_research():
    """Perform comprehensive market research"""
    logger.info("Starting comprehensive market research")
    
    workflow = ResearchWorkflow()
    
    research_topic = "Electric vehicle market trends and adoption rates in 2024"
    
    print("🔍 Starting comprehensive market research...")
    result = workflow.run(research_topic)
    
    if result["success"]:
        print("✅ Market research completed!")
        
        # Save comprehensive report
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            result["final_report"],
            "ev_market_research_2024",
            "md"
        )
        print(f"💾 {save_result}")
        
        print(f"\n📊 Research Summary:")
        print(f"- Initial findings: {len(result['initial_findings'])} characters")
        print(f"- Deep dive analysis: {len(result['deep_dive_findings'])} characters")
        print(f"- Synthesis: {len(result['synthesis'])} characters")
        print(f"- Validation: {len(result['validation'])} characters")
        
        return result
    else:
        print(f"❌ Market research failed: {result.get('error', 'Unknown error')}")
        return None

def competitive_analysis():
    """Perform competitive analysis research"""
    logger.info("Starting competitive analysis")
    
    workflow = ResearchWorkflow()
    
    research_topic = "AI chatbot platforms: comparative analysis of features, pricing, and market position"
    
    print("🏆 Starting competitive analysis...")
    result = workflow.run(research_topic)
    
    if result["success"]:
        print("✅ Competitive analysis completed!")
        
        # Extract key insights
        synthesis = result["synthesis"]
        validation = result["validation"]
        
        # Create analysis summary
        analysis_summary = f"""
# Competitive Analysis Summary

## Key Findings
{synthesis[:500]}...

## Validation Results  
{validation[:300]}...

## Research Confidence
High - Based on comprehensive multi-stage analysis
"""
        
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            analysis_summary,
            "chatbot_competitive_analysis",
            "md"
        )
        print(f"💾 {save_result}")
        
        return result
    else:
        print(f"❌ Competitive analysis failed: {result.get('error', 'Unknown error')}")
        return None

def multi_topic_research():
    """Research multiple related topics collaboratively"""
    logger.info("Starting multi-topic collaborative research")
    
    workflow = ResearchWorkflow()
    
    research_topics = [
        "Artificial intelligence in healthcare: current applications and outcomes",
        "AI ethics and regulation: global perspectives and frameworks", 
        "Machine learning in medical diagnosis: accuracy and implementation challenges",
        "Healthcare data privacy in AI systems: compliance and security"
    ]
    
    print("🤝 Starting collaborative research on multiple topics...")
    result = workflow.run_collaborative_research(research_topics)
    
    if result["success"]:
        print(f"✅ Collaborative research completed on {len(research_topics)} topics!")
        
        # Save collaborative synthesis
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            result["collaborative_synthesis"],
            "ai_healthcare_collaborative_research",
            "md"
        )
        print(f"💾 {save_result}")
        
        print(f"\n📈 Research Statistics:")
        print(f"- Topics researched: {result['total_topics']}")
        print(f"- Successful analyses: {sum(1 for r in result['individual_results'].values() if r['success'])}")
        print(f"- Total synthesis length: {len(result['collaborative_synthesis'])} characters")
        
        return result
    else:
        print("❌ Collaborative research failed")
        return None

def technology_trend_analysis():
    """Analyze technology trends"""
    logger.info("Starting technology trend analysis")
    
    research_agent = ResearchAgent()
    
    # Define claims to fact-check
    tech_claims = [
        "Quantum computing will replace classical computing within the next decade",
        "5G networks increase data speeds by 100x compared to 4G", 
        "Blockchain technology reduces transaction costs by 90%",
        "AI will automate 50% of current jobs by 2030"
    ]
    
    print("🔬 Fact-checking technology claims...")
    fact_check_result = research_agent.fact_check(tech_claims)
    
    print("✅ Fact-checking completed!")
    print(f"Results: {fact_check_result[:400]}...")
    
    # Now research broader trends
    workflow = ResearchWorkflow()
    
    trend_topic = "Emerging technology trends 2024: quantum computing, 5G, blockchain, and AI"
    
    print("\n📊 Researching broader technology trends...")
    trend_result = workflow.run(trend_topic)
    
    if trend_result["success"]:
        # Combine fact-check and trend research
        combined_analysis = f"""
# Technology Trend Analysis 2024

## Fact-Check Results
{fact_check_result}

## Comprehensive Trend Analysis
{trend_result['synthesis']}

## Validation and Recommendations
{trend_result['validation']}
"""
        
        save_tool = SaveContentTool()
        save_result = save_tool._run(
            combined_analysis,
            "technology_trends_analysis_2024",
            "md"
        )
        print(f"💾 {save_result}")
        
        return {
            "fact_check": fact_check_result,
            "trend_analysis": trend_result
        }
    else:
        print(f"❌ Trend analysis failed: {trend_result.get('error', 'Unknown error')}")
        return None

def research_source_analysis():
    """Analyze multiple sources on a topic"""
    logger.info("Starting research source analysis")
    
    research_agent = ResearchAgent()
    
    topic = "Remote work productivity"
    
    # Mock sources (in real implementation, these would be actual URLs or documents)
    sources = [
        "Harvard Business Review: Remote Work Productivity Study 2024",
        "MIT Technology Review: The Science of Remote Work Efficiency",
        "Stanford Research: Work From Home Performance Analysis",
        "Gallup Poll: Employee Engagement in Remote Settings"
    ]
    
    print("📚 Analyzing multiple sources...")
    analysis_result = research_agent.analyze_sources(sources, topic)
    
    print("✅ Source analysis completed!")
    print(f"Analysis: {analysis_result[:400]}...")
    
    # Save source analysis
    save_tool = SaveContentTool()
    save_result = save_tool._run(
        analysis_result,
        "remote_work_source_analysis",
        "md"
    )
    print(f"💾 {save_result}")
    
    return analysis_result

def main():
    """Run research analysis examples"""
    print("🔬 Research Analysis Examples")
    print("=" * 35)
    
    examples = [
        ("Comprehensive Market Research", comprehensive_market_research),
        ("Competitive Analysis", competitive_analysis),
        ("Multi-Topic Collaborative Research", multi_topic_research),
        ("Technology Trend Analysis", technology_trend_analysis),
        ("Research Source Analysis", research_source_analysis)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        print("-" * 40)
        
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
