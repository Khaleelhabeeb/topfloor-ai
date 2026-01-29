"""
Researcher Agent - Web research specialist
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from google.adk.tools import FunctionTool, google_search

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition


class ResearcherAgent(BaseAgent):
    """
    Web research specialist that searches for information,
    analyzes sources, and compiles detailed research documents.
    """
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build research tools.
        
        Returns:
            List of research tools including GoogleSearch
        """
        tools = []
        
        # Add Google Search (built-in ADK tool)
        tools.append(google_search)
        
        # Save research document tool
        @FunctionTool
        def save_research_document(
            title: str,
            content: str,
            sources: List[str],
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Save a completed research document.
            
            Args:
                title: Title of the research document
                content: Full research content (markdown formatted)
                sources: List of source URLs used
                tags: Optional tags for categorization
                
            Returns:
                Confirmation with document_id
            """
            # TODO: Integrate with artifact service in STEP 4
            document_id = f"research_{title.replace(' ', '_').lower()}"
            
            document = {
                "document_id": document_id,
                "title": title,
                "content": content,
                "sources": sources,
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "type": "research_document"
            }
            
            return {
                "status": "saved",
                "document_id": document_id,
                "title": title,
                "source_count": len(sources)
            }
        
        # Extract key findings tool
        @FunctionTool
        def extract_key_findings(
            content: str,
            num_findings: int = 5
        ) -> List[str]:
            """
            Extract key findings from research content.
            
            Args:
                content: Research content to analyze
                num_findings: Number of key findings to extract
                
            Returns:
                List of key findings
            """
            # Simple extraction - in production, use LLM for better extraction
            lines = content.split('\n')
            findings = [
                line.strip('- ').strip()
                for line in lines
                if line.strip().startswith('-') or line.strip().startswith('*')
            ]
            return findings[:num_findings]
        
        tools.extend([
            save_research_document,
            extract_key_findings
        ])
        
        return tools
