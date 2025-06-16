"""
Writing Agent - Specializes in content creation and editing
"""
from typing import Optional, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from .base_agent import BaseAgent, AgentState

class WritingAgent(BaseAgent):
    """Agent specialized in content creation and writing"""
    
    def __init__(self):
        super().__init__(
            name="writing_agent",
            role="Content Creator"
        )
    
    def process(self, state: AgentState) -> AgentState:
        """Process writing tasks"""
        self.logger.info(f"WritingAgent processing: {state.current_task}")
        
        # Prepare messages for writing task
        messages = self.prepare_messages(state)
        
        # Get research findings if available
        research_context = ""
        if "research_findings" in state.context:
            research_context = f"\nResearch findings to incorporate:\n{state.context['research_findings']}\n"
        
        # Add writing-specific instructions
        writing_prompt = f"""
        Based on the task: "{state.current_task}"
        {research_context}
        
        Create high-quality content that:
        1. Is well-structured and engaging
        2. Incorporates research findings appropriately
        3. Uses clear, professional language
        4. Follows best practices for the content type
        5. Is tailored to the target audience
        
        Provide the content along with:
        - Title/heading suggestions
        - Key points covered
        - Tone and style notes
        """
        
        messages.append(HumanMessage(content=writing_prompt))
        
        # Generate content
        writing_result = self.invoke_llm(messages)
        
        # Update state with writing output
        state.agent_outputs[self.name] = writing_result
        state.context["written_content"] = writing_result
        state.messages.append(AIMessage(content=f"Content created: {writing_result}"))
        
        # Add writing metadata
        state.metadata[f"{self.name}_completed"] = True
        state.metadata[f"{self.name}_content_length"] = len(writing_result)
        
        self.log_processing(state, writing_result)
        
        return state
    
    def create_article(self, topic: str, research_data: Optional[str] = None, 
                      target_audience: str = "general", tone: str = "professional") -> str:
        """Create an article on a specific topic"""
        
        article_prompt = f"""
        Write a comprehensive article about: {topic}
        
        Target audience: {target_audience}
        Tone: {tone}
        
        {f"Research data to incorporate: {research_data}" if research_data else ""}
        
        Structure the article with:
        1. Engaging title
        2. Introduction that hooks the reader
        3. Well-organized main sections
        4. Conclusion with key takeaways
        5. Suggest relevant subheadings
        
        Ensure the content is informative, accurate, and engaging.
        """
        
        messages = [self.get_system_message(), HumanMessage(content=article_prompt)]
        return self.invoke_llm(messages)
    
    def edit_content(self, content: str, editing_instructions: str) -> str:
        """Edit existing content based on instructions"""
        
        edit_prompt = f"""
        Please edit the following content according to these instructions:
        {editing_instructions}
        
        Original content:
        {content}
        
        Provide:
        1. The edited version
        2. Summary of changes made
        3. Explanation of improvements
        """
        
        messages = [self.get_system_message(), HumanMessage(content=edit_prompt)]
        return self.invoke_llm(messages)
    
    def create_summary(self, content: str, length: str = "medium") -> str:
        """Create a summary of given content"""
        
        length_guidelines = {
            "short": "2-3 sentences",
            "medium": "1-2 paragraphs", 
            "long": "3-4 paragraphs"
        }
        
        summary_prompt = f"""
        Create a {length} summary of the following content:
        
        {content}
        
        The summary should be {length_guidelines.get(length, "1-2 paragraphs")} and capture:
        1. Main ideas and key points
        2. Important conclusions
        3. Essential information for understanding
        """
        
        messages = [self.get_system_message(), HumanMessage(content=summary_prompt)]
        return self.invoke_llm(messages)
