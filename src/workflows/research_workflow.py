"""
Research Workflow using LangGraph
"""
from typing import Dict, Any, List
from langgraph import StateGraph, END
from src.agents import AgentState, ResearchAgent
from src.utils import get_logger

logger = get_logger("workflows.research")

class ResearchWorkflow:
    """Workflow for comprehensive research tasks"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
        
        logger.info("ResearchWorkflow initialized")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for research"""
        
        workflow = StateGraph(AgentState)
        
        # Add research steps
        workflow.add_node("initial_research", self.initial_research_step)
        workflow.add_node("deep_dive", self.deep_dive_step)
        workflow.add_node("synthesis", self.synthesis_step)
        workflow.add_node("validate", self.validation_step)
        workflow.add_node("finalize", self.finalize_step)
        
        # Define the research flow
        workflow.set_entry_point("initial_research")
        workflow.add_edge("initial_research", "deep_dive")
        workflow.add_edge("deep_dive", "synthesis")
        workflow.add_edge("synthesis", "validate")
        workflow.add_edge("validate", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def initial_research_step(self, state: AgentState) -> AgentState:
        """Perform initial broad research"""
        logger.info("Executing initial research step")
        
        # Modify the task for initial research
        original_task = state.current_task
        state.current_task = f"Conduct initial broad research on: {original_task}"
        
        state = self.research_agent.process(state)
        
        # Store initial findings
        state.context["initial_findings"] = state.agent_outputs.get("research_agent", "")
        state.current_task = original_task  # Restore original task
        
        return state
    
    def deep_dive_step(self, state: AgentState) -> AgentState:
        """Perform deep dive research on specific aspects"""
        logger.info("Executing deep dive research step")
        
        initial_findings = state.context.get("initial_findings", "")
        
        # Create deep dive task based on initial findings
        deep_dive_task = f"""
        Based on the initial research findings below, conduct a deep dive analysis on:
        {state.current_task}
        
        Initial findings:
        {initial_findings}
        
        Focus on:
        1. Detailed analysis of key points
        2. Supporting evidence and data
        3. Different perspectives and viewpoints
        4. Potential gaps or areas needing more investigation
        """
        
        state.current_task = deep_dive_task
        state = self.research_agent.process(state)
        
        # Store deep dive findings
        state.context["deep_dive_findings"] = state.agent_outputs.get("research_agent", "")
        
        return state
    
    def synthesis_step(self, state: AgentState) -> AgentState:
        """Synthesize all research findings"""
        logger.info("Executing synthesis step")
        
        initial_findings = state.context.get("initial_findings", "")
        deep_dive_findings = state.context.get("deep_dive_findings", "")
        
        synthesis_task = f"""
        Synthesize all research findings for: {state.current_task}
        
        Initial Research:
        {initial_findings}
        
        Deep Dive Research:
        {deep_dive_findings}
        
        Create a comprehensive synthesis that includes:
        1. Executive summary of key findings
        2. Main themes and patterns
        3. Supporting evidence and data
        4. Conflicting viewpoints and their resolution
        5. Implications and recommendations
        6. Areas for future research
        """
        
        state.current_task = synthesis_task
        state = self.research_agent.process(state)
        
        # Store synthesis
        state.context["research_synthesis"] = state.agent_outputs.get("research_agent", "")
        
        return state
    
    def validation_step(self, state: AgentState) -> AgentState:
        """Validate research findings"""
        logger.info("Executing validation step")
        
        synthesis = state.context.get("research_synthesis", "")
        
        validation_task = f"""
        Validate the following research synthesis for accuracy and completeness:
        
        {synthesis}
        
        Validation criteria:
        1. Factual accuracy
        2. Logical consistency
        3. Source reliability assessment
        4. Bias identification
        5. Gap analysis
        6. Confidence levels for each finding
        
        Provide validation results and recommendations for improvement.
        """
        
        state.current_task = validation_task
        state = self.research_agent.process(state)
        
        # Store validation results
        state.context["validation_results"] = state.agent_outputs.get("research_agent", "")
        
        return state
    
    def finalize_step(self, state: AgentState) -> AgentState:
        """Finalize research workflow"""
        logger.info("Finalizing research workflow")
        
        # Compile final research report
        final_report = f"""
COMPREHENSIVE RESEARCH REPORT

=== EXECUTIVE SUMMARY ===
{state.context.get('research_synthesis', '')[:500]}...

=== INITIAL FINDINGS ===
{state.context.get('initial_findings', '')}

=== DETAILED ANALYSIS ===
{state.context.get('deep_dive_findings', '')}

=== SYNTHESIS ===
{state.context.get('research_synthesis', '')}

=== VALIDATION ===
{state.context.get('validation_results', '')}

=== METADATA ===
Original Task: {state.current_task}
Research Depth: Comprehensive (4 stages)
Validation: Completed
"""
        
        state.context["final_research_report"] = final_report
        state.metadata["research_workflow_completed"] = True
        
        return state
    
    def run(self, research_topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the research workflow"""
        logger.info(f"Starting research workflow for: {research_topic}")
        
        # Initialize state
        initial_state = AgentState(
            current_task=research_topic,
            context=context or {},
            metadata={"research_workflow_started": True}
        )
        
        try:
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "research_topic": research_topic,
                "final_report": final_state.context.get("final_research_report", ""),
                "initial_findings": final_state.context.get("initial_findings", ""),
                "deep_dive_findings": final_state.context.get("deep_dive_findings", ""),
                "synthesis": final_state.context.get("research_synthesis", ""),
                "validation": final_state.context.get("validation_results", ""),
                "metadata": final_state.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in research workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "research_topic": research_topic
            }
    
    def run_collaborative_research(self, research_topics: List[str]) -> Dict[str, Any]:
        """Run collaborative research on multiple related topics"""
        logger.info(f"Starting collaborative research on {len(research_topics)} topics")
        
        research_results = {}
        combined_context = {}
        
        # Research each topic
        for i, topic in enumerate(research_topics):
            logger.info(f"Researching topic {i+1}/{len(research_topics)}: {topic}")
            
            # Use previous research as context
            result = self.run(topic, combined_context.copy())
            research_results[topic] = result
            
            # Add to combined context for next iteration
            if result["success"]:
                combined_context[f"previous_research_{i}"] = result["synthesis"]
        
        # Create collaborative synthesis
        collaborative_synthesis = self._create_collaborative_synthesis(research_results)
        
        return {
            "success": True,
            "research_topics": research_topics,
            "individual_results": research_results,
            "collaborative_synthesis": collaborative_synthesis,
            "total_topics": len(research_topics)
        }
    
    def _create_collaborative_synthesis(self, research_results: Dict[str, Any]) -> str:
        """Create a synthesis across multiple research topics"""
        
        synthesis_parts = []
        
        for topic, result in research_results.items():
            if result["success"]:
                synthesis_parts.append(f"=== {topic.upper()} ===\n{result['synthesis']}\n")
        
        combined_research = "\n".join(synthesis_parts)
        
        # Use research agent to create collaborative synthesis
        synthesis_task = f"""
        Create a collaborative synthesis across multiple research topics:
        
        {combined_research}
        
        Provide:
        1. Cross-topic themes and patterns
        2. Interconnections between topics
        3. Comprehensive insights
        4. Unified recommendations
        5. Research gaps across all topics
        """
        
        # Create temporary state for synthesis
        temp_state = AgentState(current_task=synthesis_task)
        result_state = self.research_agent.process(temp_state)
        
        return result_state.agent_outputs.get("research_agent", "Synthesis not available")
