"""
Base agent class for the Multi-Agent AI System
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.config import settings
from src.utils import get_logger

class AgentState(BaseModel):
    """Represents the state that agents pass between each other"""
    
    messages: List[BaseMessage] = Field(default_factory=list)
    current_task: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(
        self,
        name: str,
        role: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.role = role
        self.logger = get_logger(f"agent.{name}")
        
        # Get agent-specific configuration
        agent_config = settings.get_agent_config(name.lower())
        
        # Initialize LLM with configuration
        self.llm = ChatOpenAI(
            model=model or agent_config.get("model", settings.DEFAULT_MODEL),
            temperature=temperature or agent_config.get("temperature", settings.TEMPERATURE),
            max_tokens=max_tokens or agent_config.get("max_tokens", settings.MAX_TOKENS),
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.system_prompt = system_prompt or agent_config.get("system_prompt", "")
        self.tools = []
        
        self.logger.info(f"Initialized {self.name} agent with role: {self.role}")
    
    def add_tool(self, tool):
        """Add a tool to this agent's toolkit"""
        self.tools.append(tool)
        self.logger.info(f"Added tool {tool.__class__.__name__} to {self.name}")
    
    def get_system_message(self) -> SystemMessage:
        """Get the system message for this agent"""
        return SystemMessage(content=self.system_prompt)
    
    def prepare_messages(self, state: AgentState) -> List[BaseMessage]:
        """Prepare messages for the LLM call"""
        messages = [self.get_system_message()]
        
        # Add context from previous agents if available
        if state.context:
            context_msg = f"Context from previous agents: {state.context}"
            messages.append(HumanMessage(content=context_msg))
        
        # Add the current task
        if state.current_task:
            messages.append(HumanMessage(content=f"Task: {state.current_task}"))
        
        # Add any existing messages
        messages.extend(state.messages)
        
        return messages
    
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state"""
        pass
    
    def invoke_llm(self, messages: List[BaseMessage]) -> str:
        """Invoke the LLM with prepared messages"""
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Error invoking LLM for {self.name}: {str(e)}")
            raise
    
    def log_processing(self, state: AgentState, result: str):
        """Log the processing result"""
        self.logger.info(f"{self.name} processed task: {state.current_task}")
        self.logger.debug(f"{self.name} output: {result[:200]}...")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
