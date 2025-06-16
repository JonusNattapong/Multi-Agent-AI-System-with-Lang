"""
Document Intelligence Workflow for processing documents with local LLMs
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from ..agents.document_intelligence_agent import DocumentIntelligenceAgent
from ..config.settings import settings

logger = logging.getLogger(__name__)

class DocumentProcessingState(MessagesState):
    """State for document processing workflow"""
    document_path: str = ""
    document_type: str = ""
    extracted_data: List[Dict[str, Any]] = []
    processing_status: str = "pending"
    error_message: str = ""
    use_vision: bool = False
    enable_pii_masking: bool = True

class DocumentIntelligenceWorkflow:
    """Workflow for processing documents using local LLMs and document intelligence"""

    def __init__(self):
        self.agent = DocumentIntelligenceAgent()
        self.logger = logging.getLogger(__name__)
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """Create the document processing workflow graph"""
        workflow = StateGraph(DocumentProcessingState)

        # Add nodes
        workflow.add_node("validate_document", self._validate_document)
        workflow.add_node("classify_document", self._classify_document)
        workflow.add_node("process_document", self._process_document)
        workflow.add_node("handle_error", self._handle_error)

        # Add edges
        workflow.add_edge(START, "validate_document")
        workflow.add_conditional_edges(
            "validate_document",
            self._should_continue_after_validation,
            {
                "continue": "classify_document",
                "error": "handle_error"
            }
        )
        workflow.add_edge("classify_document", "process_document")
        workflow.add_conditional_edges(
            "process_document",
            self._should_end_workflow,
            {
                "end": END,
                "error": "handle_error"
            }
        )
        workflow.add_edge("handle_error", END)

        return workflow.compile()

    def _validate_document(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Validate document format and accessibility"""
        try:
            document_path = state["document_path"]
            
            if not document_path:
                state["processing_status"] = "error"
                state["error_message"] = "No document path provided"
                return state

            if not os.path.exists(document_path):
                state["processing_status"] = "error"
                state["error_message"] = f"Document not found: {document_path}"
                return state

            if not self.agent.validate_document(document_path):
                state["processing_status"] = "error"
                state["error_message"] = f"Unsupported document format: {Path(document_path).suffix}"
                return state

            state["processing_status"] = "validated"
            self.logger.info(f"Document validated: {document_path}")
            
            # Add validation message
            state["messages"].append(
                AIMessage(content=f"Document validated successfully: {Path(document_path).name}")
            )

        except Exception as e:
            state["processing_status"] = "error"
            state["error_message"] = f"Validation failed: {str(e)}"
            self.logger.error(f"Document validation failed: {e}")

        return state

    def _classify_document(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Classify the document type"""
        try:
            document_path = state["document_path"]
            document_type = self.agent.classify_document(document_path)
            
            state["document_type"] = document_type or "Unknown"
            state["processing_status"] = "classified"
            
            self.logger.info(f"Document classified as: {state['document_type']}")
            
            # Add classification message
            state["messages"].append(
                AIMessage(content=f"Document classified as: {state['document_type']}")
            )

        except Exception as e:
            state["processing_status"] = "error"
            state["error_message"] = f"Classification failed: {str(e)}"
            self.logger.error(f"Document classification failed: {e}")

        return state

    def _process_document(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Process the document and extract structured data"""
        try:
            document_path = state["document_path"]
            use_vision = state.get("use_vision", False)
            
            # Determine processing strategy based on context window
            if settings.MAX_CONTEXT_TOKENS <= 8192:
                # Use pagination for limited context models
                extracted_data = self.agent.extract_with_pagination(document_path)
                strategy_used = "pagination (limited context)"
            else:
                # Use standard processing for larger context models
                result = self.agent.process_document(document_path, use_vision=use_vision)
                extracted_data = [item.dict() if hasattr(item, 'dict') else str(item) for item in result]
                strategy_used = "standard processing"

            state["extracted_data"] = extracted_data
            state["processing_status"] = "completed"
            
            self.logger.info(f"Document processed successfully using {strategy_used}")
            self.logger.info(f"Extracted {len(extracted_data)} data items")
            
            # Add processing result message
            state["messages"].append(
                AIMessage(
                    content=f"Document processed successfully using {strategy_used}. "
                           f"Extracted {len(extracted_data)} data items."
                )
            )

        except Exception as e:
            state["processing_status"] = "error"
            state["error_message"] = f"Processing failed: {str(e)}"
            self.logger.error(f"Document processing failed: {e}")

        return state

    def _handle_error(self, state: DocumentProcessingState) -> DocumentProcessingState:
        """Handle errors in the workflow"""
        error_message = state.get("error_message", "Unknown error occurred")
        self.logger.error(f"Workflow error: {error_message}")
        
        state["messages"].append(
            AIMessage(content=f"Error: {error_message}")
        )
        
        return state

    def _should_continue_after_validation(self, state: DocumentProcessingState) -> str:
        """Determine if workflow should continue after validation"""
        return "continue" if state["processing_status"] == "validated" else "error"

    def _should_end_workflow(self, state: DocumentProcessingState) -> str:
        """Determine if workflow should end"""
        return "end" if state["processing_status"] == "completed" else "error"

    def process_document(
        self, 
        document_path: str, 
        use_vision: bool = False,
        enable_pii_masking: bool = True
    ) -> Dict[str, Any]:
        """
        Process a single document through the workflow
        
        Args:
            document_path: Path to the document to process
            use_vision: Whether to use vision-capable models
            enable_pii_masking: Whether to enable PII masking
            
        Returns:
            Dictionary containing processing results
        """
        initial_state = DocumentProcessingState(
            messages=[HumanMessage(content=f"Process document: {document_path}")],
            document_path=document_path,
            use_vision=use_vision,
            enable_pii_masking=enable_pii_masking
        )

        try:
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "status": final_state["processing_status"],
                "document_path": final_state["document_path"],
                "document_type": final_state.get("document_type", "Unknown"),
                "extracted_data": final_state.get("extracted_data", []),
                "error_message": final_state.get("error_message", ""),
                "messages": [msg.content for msg in final_state["messages"]]
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "status": "error",
                "document_path": document_path,
                "document_type": "Unknown",
                "extracted_data": [],
                "error_message": str(e),
                "messages": [f"Workflow execution failed: {str(e)}"]
            }

    def batch_process_documents(
        self, 
        document_paths: List[str],
        use_vision: bool = False,
        enable_pii_masking: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple documents in batch
        
        Args:
            document_paths: List of document paths to process
            use_vision: Whether to use vision-capable models
            enable_pii_masking: Whether to enable PII masking
            
        Returns:
            Dictionary mapping document paths to processing results
        """
        results = {}
        
        for doc_path in document_paths:
            self.logger.info(f"Processing document in batch: {doc_path}")
            result = self.process_document(doc_path, use_vision, enable_pii_masking)
            results[doc_path] = result
            
        return results

    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return self.agent.get_supported_formats()

# Convenience function for quick document processing
def process_document_with_local_llm(
    document_path: str,
    use_vision: bool = False,
    enable_pii_masking: bool = True
) -> Dict[str, Any]:
    """
    Quick function to process a document with local LLM
    
    Args:
        document_path: Path to the document
        use_vision: Whether to use vision models
        enable_pii_masking: Whether to mask PII
        
    Returns:
        Processing results
    """
    workflow = DocumentIntelligenceWorkflow()
    return workflow.process_document(document_path, use_vision, enable_pii_masking)
