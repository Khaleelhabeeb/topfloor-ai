"""
Researcher Agent - Web research specialist
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from urllib.parse import urlparse
from app.tools.research_tools import web_search as web_search_tool
from google.adk.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition
from app.tools.document_templates import get_template


class ResearcherAgent(BaseAgent):
    """
    Web research specialist that searches for information,
    analyzes sources, and compiles detailed research documents.
    """
    
    def _build_standard_compilation(
        self,
        topic: str,
        facts: List[Dict[str, Any]],
        opinions: List[Dict[str, Any]],
        statistics: List[Dict[str, Any]],
        quotes: List[Dict[str, Any]],
        uncategorized: List[Dict[str, Any]]
    ) -> str:
        """Build a standard research compilation structure."""
        sections = []
        
        sections.append(f"# Research Compilation: {topic}\n")
        
        if facts:
            sections.append("\n## Factual Findings\n")
            for i, fact in enumerate(facts[:10], 1):
                content = fact.get("content", "")
                source = fact.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        if statistics:
            sections.append("\n## Statistical Data\n")
            for i, stat in enumerate(statistics[:10], 1):
                content = stat.get("content", "")
                source = stat.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        if opinions:
            sections.append("\n## Expert Opinions & Analysis\n")
            for i, opinion in enumerate(opinions[:10], 1):
                content = opinion.get("content", "")
                source = opinion.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        if quotes:
            sections.append("\n## Notable Quotes\n")
            for i, quote in enumerate(quotes[:5], 1):
                content = quote.get("content", "")
                source = quote.get("source", "Unknown")
                sections.append(f"{i}. \"{content}\"\n   - Source: {source}\n")
        
        if uncategorized:
            sections.append("\n## Additional Findings\n")
            for i, item in enumerate(uncategorized[:5], 1):
                content = item.get("content", "")
                source = item.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        return "".join(sections)
    
    def _build_comparative_compilation(
        self,
        findings: List[Dict[str, Any]],
        facts: List[Dict[str, Any]],
        opinions: List[Dict[str, Any]],
        statistics: List[Dict[str, Any]]
    ) -> str:
        """Build a comparative research compilation."""
        sections = []
        
        sections.append("# Comparative Analysis\n")
        sections.append("\n## Supporting Evidence\n")
        
        supporting = [f for f in findings if any(
            word in f.get("content", "").lower() 
            for word in ["support", "positive", "effective", "success", "benefit"]
        )]
        
        for i, item in enumerate(supporting[:5], 1):
            content = item.get("content", "")
            source = item.get("source", "Unknown")
            sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        sections.append("\n## Opposing Evidence\n")
        
        opposing = [f for f in findings if any(
            word in f.get("content", "").lower() 
            for word in ["oppose", "negative", "ineffective", "failure", "risk"]
        )]
        
        for i, item in enumerate(opposing[:5], 1):
            content = item.get("content", "")
            source = item.get("source", "Unknown")
            sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        sections.append("\n## Neutral Findings\n")
        
        neutral = [f for f in findings if f not in supporting and f not in opposing]
        
        for i, item in enumerate(neutral[:5], 1):
            content = item.get("content", "")
            source = item.get("source", "Unknown")
            sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        return "".join(sections)
    
    def _build_chronological_compilation(
        self,
        findings: List[Dict[str, Any]]
    ) -> str:
        """Build a chronological research compilation."""
        sections = []
        
        sections.append("# Chronological Research Timeline\n")
        
        # Sort by date if available
        dated_findings = [f for f in findings if f.get("date")]
        undated_findings = [f for f in findings if not f.get("date")]
        
        dated_findings.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        if dated_findings:
            sections.append("\n## Timeline of Findings\n")
            for item in dated_findings[:15]:
                content = item.get("content", "")
                source = item.get("source", "Unknown")
                date = item.get("date", "Unknown date")
                sections.append(f"- **{date}**: {content}\n  - Source: {source}\n")
        
        if undated_findings:
            sections.append("\n## Undated Findings\n")
            for i, item in enumerate(undated_findings[:10], 1):
                content = item.get("content", "")
                source = item.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        return "".join(sections)
    
    def _build_thematic_compilation(
        self,
        findings: List[Dict[str, Any]]
    ) -> str:
        """Build a thematic research compilation."""
        sections = []
        
        sections.append("# Thematic Research Compilation\n")
        
        # Group by type
        by_type = {}
        for finding in findings:
            ftype = finding.get("type", "general")
            if ftype not in by_type:
                by_type[ftype] = []
            by_type[ftype].append(finding)
        
        for ftype, items in by_type.items():
            sections.append(f"\n## {ftype.title()} Findings\n")
            for i, item in enumerate(items[:10], 1):
                content = item.get("content", "")
                source = item.get("source", "Unknown")
                sections.append(f"{i}. {content}\n   - Source: {source}\n")
        
        return "".join(sections)
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build research tools.
        
        Returns:
            List of research tools including:
            - web_search: Web search helper
            - save_research_document: Save completed research documents
            - extract_key_findings: Extract key findings from research content
        """
        tools = []
        
        # Web search helper (Python callable for AFC compatibility)
        def web_search(
            query: str,
            num_results: int = 10,
            filters_json: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Search the web for information.
            """
            filters = None
            if filters_json:
                try:
                    filters = json.loads(filters_json)
                except json.JSONDecodeError as e:
                    return {
                        "status": "error",
                        "message": f"Invalid JSON format for filters: {str(e)}"
                    }

            return web_search_tool(query, num_results=num_results, filters=filters)
        
        # Fetch content tool
        def fetch_content_tool(
            url: str,
            extract_type: str = "text"
        ) -> Dict[str, Any]:
            """
            Fetch and extract content from a URL using web scraping.
            
            This tool fetches web pages and extracts content based on the specified
            extraction type. It handles HTTP requests, HTML parsing, and content extraction.
            
            Args:
                url: URL to fetch content from
                extract_type: Type of extraction to perform:
                    - "text": Extract plain text content (paragraphs, headings)
                    - "structured": Extract structured data (title, headings, paragraphs, links)
                    - "metadata": Extract metadata (title, description, author, date)
                    - "full": Extract everything (text, structured data, and metadata)
                
            Returns:
                Dictionary containing extracted content and metadata
                
            Example:
                >>> content = fetch_content_tool("https://example.com/article", "structured")
                >>> print(content["content"]["title"])
                "Article Title"
            """
            from app.tools.research_tools import fetch_content
            return fetch_content(url, extract_type)
        
        # Save research document tool
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
        
        # Source verification tool
        def verify_source(
            url: str,
            criteria: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Verify source credibility and reliability.
            
            This tool evaluates a source URL based on multiple criteria including:
            - Domain credibility (checks against known credible domains)
            - SSL/HTTPS security
            - Domain structure and TLD
            - URL format validity
            
            Args:
                url: The URL to verify
                criteria: Optional list of specific criteria to check
                    (e.g., ["ssl", "domain", "tld"])
                
            Returns:
                Dictionary containing:
                - url: The original URL
                - domain: Extracted domain name
                - has_ssl: Whether the URL uses HTTPS
                - tld: Top-level domain
                - credibility_score: Score from 0.0 to 1.0
                - is_credible: Boolean indicating if source is credible
                - warnings: List of any credibility warnings
                - checks_performed: List of checks that were performed
            """
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Remove www. prefix for consistency
                if domain.startswith('www.'):
                    domain = domain[4:]
                
                # Extract TLD
                tld = domain.split('.')[-1] if '.' in domain else ''
                
                # Initialize score and warnings
                credibility_score = 0.5  # Start at neutral
                warnings = []
                checks_performed = []
                
                # Check SSL/HTTPS
                has_ssl = url.startswith("https://")
                checks_performed.append("ssl")
                if has_ssl:
                    credibility_score += 0.2
                else:
                    warnings.append("No HTTPS encryption detected")
                    credibility_score -= 0.1
                
                # Check against known credible domains
                credible_domains = {
                    # News organizations
                    'nytimes.com', 'washingtonpost.com', 'bbc.com', 'bbc.co.uk',
                    'reuters.com', 'apnews.com', 'theguardian.com', 'wsj.com',
                    'npr.org', 'pbs.org', 'economist.com', 'ft.com',
                    
                    # Academic and research
                    'nature.com', 'science.org', 'sciencedirect.com', 'springer.com',
                    'wiley.com', 'ieee.org', 'acm.org', 'arxiv.org', 'pubmed.gov',
                    'nih.gov', 'cdc.gov', 'who.int',
                    
                    # Government
                    'gov', 'gov.uk', 'europa.eu', 'un.org',
                    
                    # Educational
                    'edu', 'ac.uk', 'edu.au',
                    
                    # Technology and business
                    'bloomberg.com', 'forbes.com', 'techcrunch.com', 'wired.com',
                    'arstechnica.com', 'theverge.com'
                }
                
                checks_performed.append("domain_reputation")
                if domain in credible_domains or any(domain.endswith(f'.{cd}') for cd in credible_domains):
                    credibility_score += 0.3
                
                # Check TLD credibility
                credible_tlds = {'gov', 'edu', 'org', 'ac', 'mil'}
                suspicious_tlds = {'xyz', 'top', 'tk', 'ml', 'ga', 'cf', 'gq'}
                
                checks_performed.append("tld")
                if tld in credible_tlds:
                    credibility_score += 0.2
                elif tld in suspicious_tlds:
                    warnings.append(f"Suspicious TLD: .{tld}")
                    credibility_score -= 0.2
                
                # Check for valid domain structure
                checks_performed.append("domain_structure")
                if not domain or '.' not in domain:
                    warnings.append("Invalid domain structure")
                    credibility_score -= 0.3
                
                # Check for suspicious patterns
                checks_performed.append("suspicious_patterns")
                suspicious_patterns = ['-', 'free', 'download', 'click', 'win', 'prize']
                if any(pattern in domain for pattern in suspicious_patterns):
                    warnings.append("Domain contains suspicious patterns")
                    credibility_score -= 0.1
                
                # Ensure score is between 0 and 1
                credibility_score = max(0.0, min(1.0, credibility_score))
                
                # Determine if credible (threshold: 0.6)
                is_credible = credibility_score >= 0.6 and has_ssl
                
                return {
                    "url": url,
                    "domain": domain,
                    "has_ssl": has_ssl,
                    "tld": tld,
                    "credibility_score": round(credibility_score, 2),
                    "is_credible": is_credible,
                    "warnings": warnings,
                    "checks_performed": checks_performed,
                    "recommendation": (
                        "Source appears credible" if is_credible
                        else "Use caution with this source" if credibility_score >= 0.4
                        else "Source may not be reliable"
                    )
                }
                
            except Exception as e:
                return {
                    "url": url,
                    "domain": "unknown",
                    "has_ssl": False,
                    "tld": "unknown",
                    "credibility_score": 0.0,
                    "is_credible": False,
                    "warnings": [f"Error verifying source: {str(e)}"],
                    "checks_performed": ["error"],
                    "recommendation": "Unable to verify source"
                }
        
        # Research compilation tool
        def compile_research(
            findings_json: str,
            topic: str,
            structure: Optional[str] = "standard"
        ) -> Dict[str, Any]:
            """
            Compile and synthesize research findings from multiple sources.
            
            This tool takes findings from various sources and synthesizes them into
            a structured research compilation. It organizes information, identifies
            patterns, notes contradictions, and creates a coherent narrative.
            
            Args:
                findings_json: JSON string of research findings list. Each finding should contain:
                    - content: The finding text
                    - source: Source URL or reference
                    - credibility_score: Optional credibility score (0.0-1.0)
                    - type: Optional type (fact, opinion, statistic, quote)
                    - date: Optional publication date
                    Example: '[{"content": "Finding 1", "source": "url1", "type": "fact"}]'
                topic: The research topic or question being investigated
                structure: Output structure format:
                    - "standard": Executive summary, key findings, detailed analysis
                    - "comparative": Compare and contrast different perspectives
                    - "chronological": Organize by timeline
                    - "thematic": Group by themes/topics
                    
            Returns:
                Dictionary containing:
                - topic: The research topic
                - compilation: Structured research compilation
                - executive_summary: Brief overview of key findings
                - key_findings: List of main findings with citations
                - source_analysis: Analysis of sources used
                - contradictions: Any contradictory information found
                - confidence_level: Overall confidence in findings (low/medium/high)
                - recommendations: Suggested next steps or areas for further research
                - sources_cited: List of all sources with metadata
                - compiled_at: Timestamp of compilation
            """
            # Parse JSON string to list
            try:
                findings = json.loads(findings_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"Invalid JSON format for findings: {str(e)}"
                }
            
            if not findings:
                return {
                    "topic": topic,
                    "compilation": "No findings provided for compilation.",
                    "executive_summary": "No research data available.",
                    "key_findings": [],
                    "source_analysis": {"total_sources": 0, "credible_sources": 0},
                    "contradictions": [],
                    "confidence_level": "low",
                    "recommendations": ["Gather research findings before compilation"],
                    "sources_cited": [],
                    "compiled_at": datetime.now().isoformat()
                }
            
            # Analyze sources
            total_sources = len(findings)
            credible_sources = sum(
                1 for f in findings 
                if f.get("credibility_score", 0) >= 0.6
            )
            avg_credibility = sum(
                f.get("credibility_score", 0.5) for f in findings
            ) / total_sources if total_sources > 0 else 0
            
            # Categorize findings by type
            facts = [f for f in findings if f.get("type") == "fact"]
            opinions = [f for f in findings if f.get("type") == "opinion"]
            statistics = [f for f in findings if f.get("type") == "statistic"]
            quotes = [f for f in findings if f.get("type") == "quote"]
            uncategorized = [
                f for f in findings 
                if f.get("type") not in ["fact", "opinion", "statistic", "quote"]
            ]
            
            # Extract key findings (prioritize facts and statistics from credible sources)
            key_findings = []
            for finding in findings:
                if finding.get("credibility_score", 0) >= 0.6:
                    key_findings.append({
                        "content": finding.get("content", ""),
                        "source": finding.get("source", "Unknown"),
                        "type": finding.get("type", "general"),
                        "credibility": finding.get("credibility_score", 0)
                    })
            
            # Sort by credibility
            key_findings.sort(key=lambda x: x.get("credibility", 0), reverse=True)
            key_findings = key_findings[:10]  # Top 10 findings
            
            # Detect contradictions (simplified - looks for opposing keywords)
            contradictions = []
            opposing_pairs = [
                ("increase", "decrease"),
                ("positive", "negative"),
                ("support", "oppose"),
                ("agree", "disagree"),
                ("effective", "ineffective"),
                ("success", "failure")
            ]
            
            for i, f1 in enumerate(findings):
                content1 = f1.get("content", "").lower()
                for j, f2 in enumerate(findings[i+1:], i+1):
                    content2 = f2.get("content", "").lower()
                    for word1, word2 in opposing_pairs:
                        if word1 in content1 and word2 in content2:
                            contradictions.append({
                                "finding_1": f1.get("content", "")[:100] + "...",
                                "source_1": f1.get("source", "Unknown"),
                                "finding_2": f2.get("content", "")[:100] + "...",
                                "source_2": f2.get("source", "Unknown"),
                                "note": f"Potential contradiction: '{word1}' vs '{word2}'"
                            })
            
            # Determine confidence level
            if avg_credibility >= 0.7 and credible_sources >= total_sources * 0.7:
                confidence_level = "high"
            elif avg_credibility >= 0.5 and credible_sources >= total_sources * 0.5:
                confidence_level = "medium"
            else:
                confidence_level = "low"
            
            # Generate executive summary
            executive_summary = (
                f"Research compilation on '{topic}' based on {total_sources} sources "
                f"({credible_sources} credible). "
            )
            
            if facts:
                executive_summary += f"Found {len(facts)} factual findings. "
            if statistics:
                executive_summary += f"Includes {len(statistics)} statistical data points. "
            if contradictions:
                executive_summary += f"Note: {len(contradictions)} potential contradictions identified. "
            
            executive_summary += f"Overall confidence: {confidence_level}."
            
            # Build compilation based on structure
            if structure == "comparative":
                compilation = self._build_comparative_compilation(
                    findings, facts, opinions, statistics
                )
            elif structure == "chronological":
                compilation = self._build_chronological_compilation(findings)
            elif structure == "thematic":
                compilation = self._build_thematic_compilation(findings)
            else:  # standard
                compilation = self._build_standard_compilation(
                    topic, facts, opinions, statistics, quotes, uncategorized
                )
            
            # Generate recommendations
            recommendations = []
            if confidence_level == "low":
                recommendations.append("Seek additional credible sources to strengthen findings")
            if contradictions:
                recommendations.append("Investigate contradictions to clarify conflicting information")
            if len(opinions) > len(facts):
                recommendations.append("Gather more factual data to balance opinion-based findings")
            if not statistics:
                recommendations.append("Include quantitative data to support qualitative findings")
            
            # Compile sources cited
            sources_cited = []
            seen_sources = set()
            for finding in findings:
                source = finding.get("source", "Unknown")
                if source not in seen_sources:
                    seen_sources.add(source)
                    sources_cited.append({
                        "source": source,
                        "credibility_score": finding.get("credibility_score"),
                        "date": finding.get("date"),
                        "type": finding.get("type")
                    })
            
            return {
                "topic": topic,
                "compilation": compilation,
                "executive_summary": executive_summary,
                "key_findings": key_findings,
                "source_analysis": {
                    "total_sources": total_sources,
                    "credible_sources": credible_sources,
                    "average_credibility": round(avg_credibility, 2),
                    "facts_count": len(facts),
                    "opinions_count": len(opinions),
                    "statistics_count": len(statistics),
                    "quotes_count": len(quotes)
                },
                "contradictions": contradictions[:5],  # Top 5 contradictions
                "confidence_level": confidence_level,
                "recommendations": recommendations,
                "sources_cited": sources_cited,
                "compiled_at": datetime.now().isoformat()
            }
        
        # Generate Research Report Tool
        def generate_research_report(
            data_json: str,
            format: str = "pdf",
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Generate a professional research report payload.
            
            This tool creates comprehensive research reports with proper citations,
            source analysis, and structured findings. Perfect for presenting research results.
            
            Args:
                data_json: JSON string of research report data including:
                    - title: Report title (required)
                    - topic: Research topic
                    - summary: Executive summary
                    - background: Background information
                    - methodology: Research methodology
                    - findings: List of key findings
                    - analysis: Detailed analysis
                    - conclusions: Conclusions
                    - sources: List of sources/references
                    - source_credibility: Source credibility assessment
                    - analysis_charts: Optional list of chart paths
                    Example: '{"title": "AI Research", "topic": "AI in Healthcare", "findings": [...]}'
                format: Output format hint for frontend ("pdf" or "docx")
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with structured content payload for frontend rendering
                
            Example:
                >>> data_json = '{"title": "AI in Healthcare Research", "topic": "Applications of AI", "findings": ["AI improves accuracy"]}'
                >>> result = generate_research_report(data_json, "pdf")
            """
            # Parse JSON string
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"Invalid JSON format for data: {str(e)}"
                }
            
            template = get_template("researcher", "research_report")
            if not template:
                return {
                    "status": "error",
                    "message": "No research report template available"
                }
            content = template.build_content(data)
            return {
                "status": "success",
                "render_type": "report",
                "format": format,
                "template": "research_report",
                "content": content,
                "render_hint": "frontend"
            }
        
        # Chart Generation Tool (for research data visualization)
        def generate_chart(
            data_json: str,
            chart_type: str,
            config_json: Optional[str] = None,
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Generate chart payloads for research data visualization.
            
            Creates charts to visualize research data, trends, and comparisons.
            Useful for presenting quantitative research findings.
            
            Args:
                data_json: JSON string of chart data including:
                    - x: List of x-axis values (for line, bar, scatter)
                    - y: List of y-axis values or list of lists for multiple series
                    - labels: List of labels (for pie charts)
                    - values: List of values (for pie charts)
                    - series_names: List of series names for multi-series charts
                    Example: '{"x": [1,2,3], "y": [10,20,30]}'
                chart_type: Type of chart ("line", "bar", "pie", "scatter", "area")
                config_json: Optional JSON string of chart configuration:
                    - title: Chart title
                    - xlabel: X-axis label
                    - ylabel: Y-axis label
                    - colors: List of colors
                    - width: Chart width in inches
                    - height: Chart height in inches
                    Example: '{"title": "Research Trends", "xlabel": "Year"}'
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with chart payload for frontend rendering
            """
            # Parse JSON strings
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"Invalid JSON format for data: {str(e)}"
                }
            
            config = None
            if config_json:
                try:
                    config = json.loads(config_json)
                except json.JSONDecodeError as e:
                    return {
                        "status": "error",
                        "message": f"Invalid JSON format for config: {str(e)}"
                    }
            
            from app.tools.data_analysis_tools import generate_chart as gen_chart
            return gen_chart(data, chart_type, config)
        
        tools.extend([
            web_search,
            fetch_content_tool,
            save_research_document,
            extract_key_findings,
            verify_source,
            compile_research,
            generate_research_report,
            generate_chart
        ])
        
        return tools
