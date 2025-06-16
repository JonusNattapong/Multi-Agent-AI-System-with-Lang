#!/usr/bin/env python3
"""
Basic Multi-Agent Example
Demonstrates simple agent interactions
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents import ResearchAgent, WritingAgent, ReviewAgent, AgentState
from utils import get_logger

logger = get_logger("examples.basic")

def basic_agent_interaction():
    """Demonstrate basic agent interactions"""
    logger.info("Starting basic multi-agent interaction")
    
    # Initialize agents
    research_agent = ResearchAgent()
    writing_agent = WritingAgent()
    review_agent = ReviewAgent()
    
    # Create initial state
    initial_state = AgentState(
        current_task="Create a brief overview of renewable energy",
        context={"target_length": "300 words"},
        metadata={"example": "basic_interaction"}
    )
    
    print("🔬 Step 1: Research Phase")
    research_state = research_agent.process(initial_state)
    print(f"Research completed: {research_state.agent_outputs['research_agent'][:200]}...")
    
    print("\n✍️  Step 2: Writing Phase")
    writing_state = writing_agent.process(research_state)
    print(f"Content created: {writing_state.agent_outputs['writing_agent'][:200]}...")
    
    print("\n📝 Step 3: Review Phase")
    final_state = review_agent.process(writing_state)
    print(f"Review completed: {final_state.agent_outputs['review_agent'][:200]}...")
    
    return final_state

def agent_with_tools_example():
    """Demonstrate agents with tools"""
    from tools import WebSearchTool, SaveContentTool
    
    logger.info("Starting agent with tools example")
    
    # Create research agent with tools
    research_agent = ResearchAgent()
    research_agent.add_tool(WebSearchTool())
    research_agent.add_tool(SaveContentTool())
    
    # Create task
    state = AgentState(
        current_task="Research latest developments in quantum computing",
        context={"depth": "comprehensive", "save_results": True}
    )
    
    print("🔍 Research agent with tools working...")
    result_state = research_agent.process(state)
    
    print(f"✅ Research with tools completed")
    print(f"Output: {result_state.agent_outputs['research_agent'][:300]}...")
    
    return result_state

def custom_agent_chain():
    """Demonstrate custom agent processing chain"""
    logger.info("Starting custom agent chain")
    
    agents = [
        ("Research", ResearchAgent()),
        ("Writing", WritingAgent()),
        ("Review", ReviewAgent())
    ]
    
    # Initial task
    state = AgentState(
        current_task="Explain machine learning to beginners",
        context={"audience": "non-technical", "format": "blog post"}
    )
    
    # Process through agent chain
    for step, (name, agent) in enumerate(agents, 1):
        print(f"\n🔄 Step {step}: {name} Agent")
        state = agent.process(state)
        print(f"✅ {name} agent completed")
    
    print("\n🎉 Agent chain completed!")
    print("\n📊 Final Results:")
    for agent_name, output in state.agent_outputs.items():
        print(f"\n{agent_name}: {output[:150]}...")
    
    return state

def main():
    """Run basic multi-agent examples"""
    print("🤖 Basic Multi-Agent Examples")
    print("=" * 40)
    
    examples = [
        ("Basic Agent Interaction", basic_agent_interaction),
        ("Agent with Tools", agent_with_tools_example),
        ("Custom Agent Chain", custom_agent_chain)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
        print("-" * 30)
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
