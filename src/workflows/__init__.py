"""
Workflows package initialization
"""
from .content_creation import ContentCreationWorkflow
from .research_workflow import ResearchWorkflow
from .document_intelligence_workflow import DocumentIntelligenceWorkflow, process_document_with_local_llm

__all__ = [
    "ContentCreationWorkflow",
    "ResearchWorkflow",
    "DocumentIntelligenceWorkflow",
    "process_document_with_local_llm"
]
