"""
Research Agent - Specializes in information gathering and analysis
"""
from typing import List
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from .base_agent import BaseAgent, AgentState

class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering"""
    
    def __init__(self):
        super().__init__(
            name="research_agent",
            role="Research Specialist"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Process research tasks"""
        self.logger.info(f"ResearchAgent processing: {state.current_task}")
        
        # Prepare messages for research task
        messages = self.prepare_messages(state)
        
        # Add research-specific instructions
        research_prompt = f"""
        Based on the task: "{state.current_task}"
        
        Please conduct thorough research and provide:
        1. Key information and facts
        2. Multiple perspectives on the topic
        3. Relevant data and statistics
        4. Important considerations
        5. Recommendations for further investigation
        
        Structure your response clearly and cite your reasoning.
        """
        
        messages.append(HumanMessage(content=research_prompt))
        
        # Get research results
        research_result = self.invoke_llm(messages)
        
        # Update state with research findings
        state.agent_outputs[self.name] = research_result
        state.context["research_findings"] = research_result
        state.messages.append(AIMessage(content=f"Research completed: {research_result}"))
        
        # Add research metadata
        state.metadata[f"{self.name}_completed"] = True
        state.metadata[f"{self.name}_findings_length"] = len(research_result)
        
        self.log_processing(state, research_result)
        
        return state
    
    def analyze_sources(self, sources: List[str], topic: str) -> str:
        """Analyze multiple sources for a given topic"""
        analysis_prompt = f"""
        Analyze the following sources related to "{topic}":
        
        {chr(10).join([f"Source {i+1}: {source}" for i, source in enumerate(sources)])}
        
        Provide:
        1. Summary of key points from each source
        2. Comparison of different perspectives
        3. Identification of consensus and contradictions
        4. Overall synthesis of information
        """
        
        messages = [self.get_system_message(), HumanMessage(content=analysis_prompt)]
        return self.invoke_llm(messages)
    
    def fact_check(self, claims: List[str]) -> str:
        """Fact-check a list of claims"""
        fact_check_prompt = f"""
        Please fact-check the following claims:
        
        {chr(10).join([f"Claim {i+1}: {claim}" for i, claim in enumerate(claims)])}
        
        For each claim, provide:
        1. Verification status (True/False/Uncertain)
        2. Supporting evidence or contradictions
        3. Confidence level in your assessment
        4. Recommendations for further verification
        """
        
        messages = [self.get_system_message(), HumanMessage(content=fact_check_prompt)]
        return self.invoke_llm(messages)
