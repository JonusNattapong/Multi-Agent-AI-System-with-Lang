"""
Content Creation Workflow using LangGraph
"""
from typing import Dict, Any, List
from langgraph import StateGraph, END
from src.agents import AgentState, ResearchAgent, WritingAgent, ReviewAgent
from src.utils import get_logger

logger = get_logger("workflows.content_creation")

class ContentCreationWorkflow:
    """Workflow for creating content through research, writing, and review"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.review_agent = ReviewAgent()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
        
        logger.info("ContentCreationWorkflow initialized")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Define the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("research", self.research_step)
        workflow.add_node("write", self.write_step)
        workflow.add_node("review", self.review_step)
        workflow.add_node("finalize", self.finalize_step)
        
        # Define the flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", "review")
        workflow.add_edge("review", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def research_step(self, state: AgentState) -> AgentState:
        """Execute research step"""
        logger.info("Executing research step")
        return self.research_agent.process(state)
    
    def write_step(self, state: AgentState) -> AgentState:
        """Execute writing step"""
        logger.info("Executing writing step")
        return self.writing_agent.process(state)
    
    def review_step(self, state: AgentState) -> AgentState:
        """Execute review step"""
        logger.info("Executing review step")
        return self.review_agent.process(state)
    
    def finalize_step(self, state: AgentState) -> AgentState:
        """Finalize the workflow"""
        logger.info("Finalizing workflow")
        
        # Compile final results
        final_content = state.context.get("written_content", "")
        review_feedback = state.context.get("review_feedback", "")
        
        final_result = f"""
CONTENT CREATION WORKFLOW COMPLETE

=== FINAL CONTENT ===
{final_content}

=== REVIEW FEEDBACK ===
{review_feedback}

=== WORKFLOW METADATA ===
Task: {state.current_task}
Research completed: {state.metadata.get('research_agent_completed', False)}
Writing completed: {state.metadata.get('writing_agent_completed', False)}
Review completed: {state.metadata.get('review_agent_completed', False)}
"""
        
        state.context["final_result"] = final_result
        state.metadata["workflow_completed"] = True
        
        logger.info("Content creation workflow completed successfully")
        return state
    
    def run(self, task: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the content creation workflow"""
        logger.info(f"Starting content creation workflow for task: {task}")
        
        # Initialize state
        initial_state = AgentState(
            current_task=task,
            context=initial_context or {},
            metadata={"workflow_started": True}
        )
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "final_content": final_state.context.get("written_content", ""),
                "review_feedback": final_state.context.get("review_feedback", ""),
                "research_findings": final_state.context.get("research_findings", ""),
                "full_result": final_state.context.get("final_result", ""),
                "metadata": final_state.metadata,
                "agent_outputs": final_state.agent_outputs
            }
            
        except Exception as e:
            logger.error(f"Error in content creation workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": {}
            }
    
    def run_with_feedback_loop(self, task: str, max_iterations: int = 3) -> Dict[str, Any]:
        """Run workflow with iterative feedback and improvement"""
        logger.info(f"Starting iterative content creation for: {task}")
        
        iteration = 0
        current_content = ""
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Content creation iteration {iteration}")
            
            # Prepare context with previous iteration results
            context = {}
            if current_content:
                context["previous_content"] = current_content
                context["iteration"] = iteration
            
            # Run workflow
            result = self.run(f"Iteration {iteration}: {task}", context)
            
            if not result["success"]:
                break
                
            current_content = result["final_content"]
            
            # Check if review indicates completion
            review_feedback = result["review_feedback"]
            if "approved" in review_feedback.lower() or "excellent" in review_feedback.lower():
                logger.info(f"Content approved after {iteration} iterations")
                break
        
        return {
            "success": True,
            "iterations": iteration,
            "final_content": current_content,
            "improvement_history": []  # Could track changes between iterations
        }
