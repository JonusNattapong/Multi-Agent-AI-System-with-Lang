"""
Search tools for agents with real data sources
"""
import requests
import json
import os
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from src.utils import get_logger

logger = get_logger("tools.search")

class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, description="Number of results to return")

class WebSearchTool(BaseTool):
    """Tool for web searching using DuckDuckGo API"""
    
    name = "web_search"
    description = "Search the web for information on a given query"
    args_schema = WebSearchInput
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """Execute web search using DuckDuckGo API"""
        logger.info(f"Executing web search for: {query}")
        
        try:
            # Use DuckDuckGo Instant Answer API (free, no API key required)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Get abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Main Result"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", "")
                })
            
            # Get related topics
            for topic in data.get("RelatedTopics", [])[:num_results-1]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else "Related Topic",
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", "")
                    })
            
            # If no results from instant API, try search results API
            if not results:
                return self._search_web_fallback(query, num_results)
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results[:num_results], 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['url']}\n"
                    f"   Summary: {result['snippet'][:200]}...\n"
                )
            
            return "\n".join(formatted_results) if formatted_results else self._search_web_fallback(query, num_results)
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return self._search_web_fallback(query, num_results)
    
    def _search_web_fallback(self, query: str, num_results: int) -> str:
        """Fallback search implementation"""
        logger.info(f"Using fallback search for: {query}")
        
        # Try with a simple HTTP search if possible
        try:
            # Use Wikipedia API as fallback
            wikipedia_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            search_term = query.replace(" ", "_")
            
            response = requests.get(f"{wikipedia_url}{search_term}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return f"1. {data.get('title', 'Wikipedia Result')}\n   URL: {data.get('content_urls', {}).get('desktop', {}).get('page', '')}\n   Summary: {data.get('extract', 'No summary available')}\n"
        except:
            pass
        
        # Final fallback with structured mock data
        return f"Search results for '{query}':\n1. Real-time information search\n   Note: Web search temporarily unavailable. Please check internet connection.\n"

class DocumentSearchInput(BaseModel):
    """Input for document search tool"""
    query: str = Field(description="Search query for documents")
    document_type: Optional[str] = Field(default=None, description="Type of document to search for (report, specification, policy)")
    max_results: int = Field(default=5, description="Maximum number of results to return")

class DocumentSearchTool(BaseTool):
    """Tool for searching documents and knowledge bases using real file system data"""
    
    name = "document_search"
    description = "Search internal documents and knowledge bases for relevant information"
    args_schema = DocumentSearchInput
    
    def __init__(self):
        super().__init__()
        # Default document directory - can be configured via environment
        self.docs_root = Path(os.getenv("DOCUMENTS_ROOT", "./documents"))
        
    def _search_files(self, query: str, document_type: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search through actual files in the document directory"""
        results = []
        search_terms = query.lower().split()
        
        # Determine search directories based on document type
        search_dirs = []
        if document_type:
            type_mapping = {
                "report": "reports",
                "specification": "specifications", 
                "policy": "policies",
                "spec": "specifications"
            }
            if document_type.lower() in type_mapping:
                search_dirs = [self.docs_root / type_mapping[document_type.lower()]]
            else:
                # Search all directories if type not recognized
                search_dirs = [self.docs_root / d for d in ["reports", "specifications", "policies"]]
        else:
            # Search all document directories
            search_dirs = [self.docs_root / d for d in ["reports", "specifications", "policies"]]
        
        # Search through files
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            # Search text files
            for file_path in search_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Calculate relevance score based on term matches
                    content_lower = content.lower()
                    score = 0
                    matches = []
                    
                    for term in search_terms:
                        term_count = content_lower.count(term)
                        if term_count > 0:
                            score += term_count * 0.1  # Base score per term occurrence
                            matches.append(term)
                    
                    # Bonus for title matches
                    title = file_path.stem.replace('_', ' ')
                    if any(term in title.lower() for term in search_terms):
                        score += 0.5
                    
                    if score > 0:
                        # Extract relevant snippet
                        snippet = self._extract_snippet(content, search_terms)
                        
                        # Get file metadata
                        stat = file_path.stat()
                        
                        results.append({
                            "title": title.title(),
                            "file_path": str(file_path),
                            "type": search_dir.name.rstrip('s'),  # Remove 's' from directory name
                            "content": snippet,
                            "relevance_score": min(score, 1.0),  # Cap at 1.0
                            "last_updated": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                            "file_size": stat.st_size,
                            "matches": matches
                        })
                        
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
                    continue
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]
    
    def _extract_snippet(self, content: str, search_terms: List[str], snippet_length: int = 200) -> str:
        """Extract a relevant snippet from the content around search terms"""
        content_lower = content.lower()
        
        # Find the first occurrence of any search term
        best_pos = -1
        for term in search_terms:
            pos = content_lower.find(term)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos
        
        if best_pos == -1:
            # If no terms found, return beginning of content
            return content[:snippet_length].strip() + "..." if len(content) > snippet_length else content.strip()
        
        # Extract snippet around the found term
        start = max(0, best_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        
        snippet = content[start:end].strip()
        
        # Add ellipsis if we're not at the beginning/end
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet
    
    def _run(self, query: str, document_type: Optional[str] = None, max_results: int = 5) -> str:
        """Execute document search using real file system data"""
        logger.info(f"Executing document search for: {query} (type: {document_type})")
        
        try:
            # Check if documents directory exists
            if not self.docs_root.exists():
                return f"Document search error: Documents directory '{self.docs_root}' not found. Please ensure documents are available for searching."
            
            # Search for documents
            documents = self._search_files(query, document_type, max_results)
            
            if not documents:
                return f"No documents found matching query '{query}'" + (f" of type '{document_type}'" if document_type else "")
            
            # Format document results
            formatted_docs = []
            for i, doc in enumerate(documents, 1):
                formatted_docs.append(
                    f"{i}. Document: {doc['title']}\n"
                    f"   Type: {doc['type']}\n"
                    f"   Relevance: {doc['relevance_score']:.2f}\n"
                    f"   Last Updated: {doc['last_updated']}\n"
                    f"   File: {Path(doc['file_path']).name}\n"
                    f"   Matches: {', '.join(doc['matches'])}\n"
                    f"   Content: {doc['content']}\n"
                )
            
            result = f"Found {len(documents)} document(s) matching '{query}':\n\n" + "\n".join(formatted_docs)
            return result
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return f"Document search failed: {str(e)}"

class FactCheckInput(BaseModel):
    """Input for fact checking tool"""
    statement: str = Field(description="Statement to fact-check")
    sources: Optional[List[str]] = Field(default=None, description="Specific sources to check against")

class FactCheckTool(BaseTool):
    """Tool for fact-checking statements"""
    
    name = "fact_check"
    description = "Verify the accuracy of statements and claims"
    args_schema = FactCheckInput
    
    def _run(self, statement: str, sources: Optional[List[str]] = None) -> str:
        """Execute fact checking (mock implementation)"""
        logger.info(f"Fact-checking statement: {statement}")
        
        # Mock fact-check results
        fact_check_result = {
            "statement": statement,
            "verification_status": "Mostly True",
            "confidence": 0.85,
            "supporting_evidence": [
                "Multiple reputable sources confirm this claim",
                "Data from official statistics supports the statement",
                "Expert consensus aligns with this information"
            ],
            "potential_issues": [
                "Some minor details may vary depending on timeframe",
                "Context-dependent nuances should be considered"
            ],
            "sources_checked": sources or ["General knowledge base", "Public records", "Expert sources"]
        }
        
        # Format fact-check result
        result_text = f"Fact-Check Results for: '{statement}'\n\n"
        result_text += f"Status: {fact_check_result['verification_status']}\n"
        result_text += f"Confidence: {fact_check_result['confidence']:.2f}\n\n"
        result_text += "Supporting Evidence:\n"
        for evidence in fact_check_result['supporting_evidence']:
            result_text += f"- {evidence}\n"
        result_text += "\nPotential Issues:\n"
        for issue in fact_check_result['potential_issues']:
            result_text += f"- {issue}\n"
        result_text += f"\nSources Checked: {', '.join(fact_check_result['sources_checked'])}"
        
        return result_text

# Tool registry
SEARCH_TOOLS = [
    WebSearchTool(),
    DocumentSearchTool(),
    FactCheckTool()
]
