"""
Review Agent - Specializes in quality assurance and content review
"""
from typing import List, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from .base_agent import BaseAgent, AgentState

class ReviewAgent(BaseAgent):
    """Agent specialized in content review and quality assurance"""
    
    def __init__(self):
        super().__init__(
            name="review_agent",
            role="Quality Assurance Specialist"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Process review tasks"""
        self.logger.info(f"ReviewAgent processing: {state.current_task}")
        
        # Prepare messages for review task
        messages = self.prepare_messages(state)
        
        # Get content to review
        content_to_review = ""
        if "written_content" in state.context:
            content_to_review = state.context["written_content"]
        elif "research_findings" in state.context:
            content_to_review = state.context["research_findings"]
        
        # Add review-specific instructions
        review_prompt = f"""
        Based on the task: "{state.current_task}"
        
        Please review the following content:
        {content_to_review}
        
        Provide a comprehensive review covering:
        1. Content accuracy and completeness
        2. Grammar, spelling, and language quality
        3. Structure and organization
        4. Clarity and readability
        5. Consistency and flow
        6. Adherence to requirements
        7. Specific suggestions for improvement
        8. Overall quality score (1-10)
        
        Be constructive and specific in your feedback.
        """
        
        messages.append(HumanMessage(content=review_prompt))
        
        # Generate review
        review_result = self.invoke_llm(messages)
        
        # Update state with review
        state.agent_outputs[self.name] = review_result
        state.context["review_feedback"] = review_result
        state.messages.append(AIMessage(content=f"Review completed: {review_result}"))
        
        # Add review metadata
        state.metadata[f"{self.name}_completed"] = True
        state.metadata["review_completed"] = True
        
        self.log_processing(state, review_result)
        
        return state
    
    def detailed_review(self, content: str, criteria: List[str]) -> Dict[str, Any]:
        """Perform a detailed review based on specific criteria"""
        
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        
        review_prompt = f"""
        Please conduct a detailed review of the following content based on these criteria:
        {criteria_text}
        
        Content to review:
        {content}
        
        For each criterion, provide:
        1. Assessment (Excellent/Good/Fair/Poor)
        2. Specific observations
        3. Suggestions for improvement
        4. Score (1-10)
        
        Also provide:
        - Overall assessment
        - Top 3 strengths
        - Top 3 areas for improvement
        - Final recommendation
        """
        
        messages = [self.get_system_message(), HumanMessage(content=review_prompt)]
        result = self.invoke_llm(messages)
        
        return {
            "detailed_review": result,
            "criteria_used": criteria,
            "review_type": "detailed"
        }
    
    def quick_review(self, content: str) -> str:
        """Perform a quick review focusing on main issues"""
        
        quick_prompt = f"""
        Perform a quick review of this content, focusing on:
        1. Major issues or errors
        2. Overall quality assessment
        3. Top 3 improvement suggestions
        
        Content:
        {content}
        
        Provide a concise but helpful review.
        """
        
        messages = [self.get_system_message(), HumanMessage(content=quick_prompt)]
        return self.invoke_llm(messages)
    
    def compare_versions(self, version1: str, version2: str) -> str:
        """Compare two versions of content"""
        
        compare_prompt = f"""
        Compare these two versions of content and provide:
        1. Key differences between versions
        2. Improvements in version 2
        3. Any regressions or issues
        4. Recommendation on which version is better
        
        Version 1:
        {version1}
        
        Version 2:
        {version2}
        """
        
        messages = [self.get_system_message(), HumanMessage(content=compare_prompt)]
        return self.invoke_llm(messages)
    
    def final_approval(self, content: str, requirements: List[str]) -> Dict[str, Any]:
        """Provide final approval assessment"""
        
        requirements_text = "\n".join([f"- {req}" for req in requirements])
        
        approval_prompt = f"""
        Assess if this content meets the requirements for final approval:
        
        Requirements:
        {requirements_text}
        
        Content:
        {content}
        
        Provide:
        1. Pass/Fail for each requirement
        2. Overall approval status (APPROVED/NEEDS_REVISION/REJECTED)
        3. Justification for decision
        4. If not approved, specific steps needed for approval
        """
        
        messages = [self.get_system_message(), HumanMessage(content=approval_prompt)]
        result = self.invoke_llm(messages)
        
        return {
            "approval_assessment": result,
            "requirements_checked": requirements,
            "review_type": "final_approval"
        }
