"""
Research Tools - Tools for web research, information gathering, and source verification

This module provides tools for the Researcher Agent to perform:
- Web search for information
- Content fetching from URLs
- Source credibility verification
- Research compilation and synthesis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse
import re
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def validate_string_not_empty(value: str, field_name: str) -> Optional[Dict[str, Any]]:
    """
    Validate that a string is not empty
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error dict if invalid, None if valid
    """
    if not value or not isinstance(value, str) or not value.strip():
        return {
            "status": "error",
            "message": f"{field_name} is required and must be a non-empty string"
        }
    
    return None


def web_search(
    query: str,
    num_results: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Search the web for information using Google Search via ADK.
    
    This function provides a structured interface to Google Search functionality.
    The actual search is performed by the ADK's google_search tool which is
    integrated directly into the Researcher Agent.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 10, max: 50)
        filters: Optional filters for search results:
            - date_range: Filter by date ('day', 'week', 'month', 'year')
            - site: Limit search to specific site (e.g., 'site:nytimes.com')
            - filetype: Filter by file type (e.g., 'pdf', 'doc')
            - language: Language code (e.g., 'en', 'es')
        
    Returns:
        Dictionary containing:
        - query: The search query used
        - num_results: Number of results requested
        - filters: Any filters applied
        - status: "success" or "error"
        - message: Informational message
        - timestamp: When the search was performed
        
    Example:
        >>> results = web_search("climate change research", num_results=5)
        >>> print(results["status"])
        "success"
        
    Note:
        This function validates inputs and provides a structured response format.
        The actual Google Search is performed by the google_search tool from
        google.adk.tools, which is integrated into the Researcher Agent's tools.
        
        The google_search tool from ADK handles:
        - Making API calls to Google Search
        - Parsing and formatting results
        - Rate limiting and error handling
        - Returning structured search results with titles, URLs, and snippets
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(query, "query")
        if validation_error:
            return validation_error
        
        # Validate num_results
        if not isinstance(num_results, int) or num_results < 1:
            return {
                "status": "error",
                "message": f"num_results must be a positive integer, got {num_results}"
            }
        
        if num_results > 50:
            num_results = 50
            logger.warning("num_results capped at 50")
        
        filters = filters or {}
        
        # Build enhanced query with filters
        enhanced_query = query
        
        if filters.get("site"):
            enhanced_query += f" site:{filters['site']}"
        
        if filters.get("filetype"):
            enhanced_query += f" filetype:{filters['filetype']}"
        
        if filters.get("date_range"):
            # Google Search supports date ranges via query parameters
            date_filter = filters['date_range']
            if date_filter in ['day', 'week', 'month', 'year']:
                logger.info(f"Date filter '{date_filter}' will be applied by google_search tool")
        
        logger.info(f"Web search prepared for: {enhanced_query} (num_results={num_results})")
        
        return {
            "query": enhanced_query,
            "original_query": query,
            "num_results": num_results,
            "filters": filters,
            "status": "success",
            "message": (
                f"Search query prepared: '{enhanced_query}'. "
                "The google_search tool from ADK will execute this search and return "
                "structured results with titles, URLs, snippets, and metadata."
            ),
            "timestamp": datetime.now().isoformat(),
            "integration": "google_search tool from google.adk.tools",
            "note": (
                "This function validates inputs and prepares the query. "
                "The Researcher Agent uses the google_search tool from ADK "
                "to perform the actual search operation."
            )
        }
    
    except Exception as e:
        logger.error(f"Error preparing web search: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to prepare web search: {str(e)}",
            "query": query,
            "timestamp": datetime.now().isoformat()
        }


def fetch_content(
    url: str,
    extract_type: str = "text"
) -> Dict[str, Any]:
    """
    Fetch and extract content from a URL using BeautifulSoup.
    
    This function fetches web pages and extracts content based on the specified
    extraction type. It handles HTTP requests, HTML parsing, and content extraction
    with proper error handling and timeout management.
    
    Args:
        url: URL to fetch content from
        extract_type: Type of extraction to perform:
            - "text": Extract plain text content (paragraphs, headings)
            - "structured": Extract structured data (title, headings, paragraphs, links)
            - "metadata": Extract metadata (title, description, author, date)
            - "full": Extract everything (text, structured data, and metadata)
        
    Returns:
        Dictionary containing extracted content and metadata:
        - url: The fetched URL
        - extract_type: Type of extraction performed
        - status: "success" or "error"
        - content: Extracted content (varies by extract_type)
        - metadata: Additional metadata about the page
        - timestamp: When the content was fetched
        
    Example:
        >>> content = fetch_content("https://example.com/article", "structured")
        >>> print(content["content"]["title"])
        "Article Title"
        >>> print(len(content["content"]["paragraphs"]))
        10
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(url, "url")
        if validation_error:
            return validation_error
        
        validation_error = validate_string_not_empty(extract_type, "extract_type")
        if validation_error:
            return validation_error
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {
                    "status": "error",
                    "message": f"Invalid URL format: {url}",
                    "url": url
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse URL: {str(e)}",
                "url": url
            }
        
        # Validate extract_type
        valid_types = ["text", "structured", "metadata", "full"]
        if extract_type not in valid_types:
            return {
                "status": "error",
                "message": f"Invalid extract_type: {extract_type}. Valid types: {', '.join(valid_types)}",
                "url": url
            }
        
        logger.info(f"Fetching content from {url} (extract_type={extract_type})")
        
        # Fetch the webpage with timeout and proper headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException:
            return {
                "status": "error",
                "message": f"Request timeout while fetching {url}",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        except httpx.RequestError as e:
            return {
                "status": "error",
                "message": f"Request error: {str(e)}",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract content based on type
        content = {}
        
        if extract_type in ["text", "full"]:
            # Extract plain text content
            text_content = _extract_text_content(soup)
            if extract_type == "text":
                content = text_content
            else:
                content["text"] = text_content
        
        if extract_type in ["structured", "full"]:
            # Extract structured data
            structured_content = _extract_structured_content(soup)
            if extract_type == "structured":
                content = structured_content
            else:
                content["structured"] = structured_content
        
        if extract_type in ["metadata", "full"]:
            # Extract metadata
            metadata_content = _extract_metadata(soup, url)
            if extract_type == "metadata":
                content = metadata_content
            else:
                content["metadata"] = metadata_content
        
        # Build response
        result = {
            "url": url,
            "extract_type": extract_type,
            "content": content,
            "status": "success",
            "message": f"Successfully fetched and extracted content from {url}",
            "timestamp": datetime.now().isoformat(),
            "response_metadata": {
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": len(response.text)
            }
        }
        
        logger.info(f"Successfully fetched content from {url}")
        return result
    
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to fetch content: {str(e)}",
            "url": url,
            "timestamp": datetime.now().isoformat()
        }


def _extract_text_content(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract plain text content from HTML.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Dictionary with extracted text content
    """
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Extract title
    title = soup.find('title')
    title_text = title.get_text().strip() if title else ""
    
    # Extract all paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if text and len(text) > 20:  # Filter out very short paragraphs
            paragraphs.append(text)
    
    # Extract headings
    headings = []
    for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for heading in soup.find_all(heading_tag):
            text = heading.get_text().strip()
            if text:
                headings.append({
                    "level": heading_tag,
                    "text": text
                })
    
    # Get full text (cleaned)
    full_text = soup.get_text(separator=' ', strip=True)
    # Clean up multiple spaces and newlines
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    
    return {
        "title": title_text,
        "paragraphs": paragraphs,
        "headings": headings,
        "full_text": full_text[:5000],  # Limit to first 5000 chars
        "paragraph_count": len(paragraphs),
        "heading_count": len(headings),
        "word_count": len(full_text.split())
    }


def _extract_structured_content(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract structured data from HTML.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Dictionary with structured content
    """
    # Extract title
    title = soup.find('title')
    title_text = title.get_text().strip() if title else ""
    
    # Extract main heading (h1)
    h1 = soup.find('h1')
    main_heading = h1.get_text().strip() if h1 else ""
    
    # Extract all headings with hierarchy
    headings = []
    for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for heading in soup.find_all(heading_tag):
            text = heading.get_text().strip()
            if text:
                headings.append({
                    "level": int(heading_tag[1]),
                    "tag": heading_tag,
                    "text": text
                })
    
    # Extract paragraphs with context
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if text and len(text) > 20:
            # Try to find parent section heading
            parent_heading = None
            for parent in p.parents:
                heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if heading:
                    parent_heading = heading.get_text().strip()
                    break
            
            paragraphs.append({
                "text": text,
                "section": parent_heading,
                "length": len(text)
            })
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().strip()
        if text and href:
            links.append({
                "text": text,
                "url": href,
                "is_external": href.startswith('http')
            })
    
    # Extract images
    images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        if src:
            images.append({
                "src": src,
                "alt": alt,
                "title": img.get('title', '')
            })
    
    # Extract lists
    lists = []
    for ul in soup.find_all(['ul', 'ol']):
        items = [li.get_text().strip() for li in ul.find_all('li', recursive=False)]
        if items:
            lists.append({
                "type": ul.name,
                "items": items,
                "item_count": len(items)
            })
    
    return {
        "title": title_text,
        "main_heading": main_heading,
        "headings": headings,
        "paragraphs": paragraphs[:50],  # Limit to first 50 paragraphs
        "links": links[:100],  # Limit to first 100 links
        "images": images[:50],  # Limit to first 50 images
        "lists": lists[:20],  # Limit to first 20 lists
        "counts": {
            "headings": len(headings),
            "paragraphs": len(paragraphs),
            "links": len(links),
            "images": len(images),
            "lists": len(lists)
        }
    }


def _extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extract metadata from HTML.
    
    Args:
        soup: BeautifulSoup object
        url: Original URL
        
    Returns:
        Dictionary with metadata
    """
    metadata = {
        "url": url,
        "domain": urlparse(url).netloc
    }
    
    # Extract title
    title = soup.find('title')
    if title:
        metadata["title"] = title.get_text().strip()
    
    # Extract meta tags
    meta_tags = {}
    
    # Description
    description = soup.find('meta', attrs={'name': 'description'})
    if description and description.get('content'):
        meta_tags["description"] = description['content']
    
    # Keywords
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords and keywords.get('content'):
        meta_tags["keywords"] = keywords['content']
    
    # Author
    author = soup.find('meta', attrs={'name': 'author'})
    if author and author.get('content'):
        meta_tags["author"] = author['content']
    
    # Publication date
    pub_date = soup.find('meta', attrs={'property': 'article:published_time'})
    if not pub_date:
        pub_date = soup.find('meta', attrs={'name': 'date'})
    if not pub_date:
        pub_date = soup.find('meta', attrs={'name': 'publish_date'})
    if pub_date and pub_date.get('content'):
        meta_tags["published_date"] = pub_date['content']
    
    # Open Graph tags
    og_tags = {}
    for og in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
        if og.get('content'):
            property_name = og['property'].replace('og:', '')
            og_tags[property_name] = og['content']
    
    if og_tags:
        meta_tags["open_graph"] = og_tags
    
    # Twitter Card tags
    twitter_tags = {}
    for twitter in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
        if twitter.get('content'):
            property_name = twitter['name'].replace('twitter:', '')
            twitter_tags[property_name] = twitter['content']
    
    if twitter_tags:
        meta_tags["twitter_card"] = twitter_tags
    
    # Language
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        metadata["language"] = html_tag['lang']
    
    # Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical and canonical.get('href'):
        metadata["canonical_url"] = canonical['href']
    
    metadata["meta_tags"] = meta_tags
    
    return metadata


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
        
    Example:
        >>> result = verify_source("https://www.nytimes.com/article")
        >>> print(result["is_credible"])
        True
    """
    try:
        # Validate inputs
        validation_error = validate_string_not_empty(url, "url")
        if validation_error:
            return validation_error
        
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
            ),
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error verifying source {url}: {str(e)}")
        return {
            "url": url,
            "domain": "unknown",
            "has_ssl": False,
            "tld": "unknown",
            "credibility_score": 0.0,
            "is_credible": False,
            "warnings": [f"Error verifying source: {str(e)}"],
            "checks_performed": ["error"],
            "recommendation": "Unable to verify source",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }


def compile_research(
    findings: List[Dict[str, Any]],
    topic: str,
    structure: Optional[str] = "standard"
) -> Dict[str, Any]:
    """
    Compile and synthesize research findings from multiple sources.
    
    This tool takes findings from various sources and synthesizes them into
    a structured research compilation. It organizes information, identifies
    patterns, notes contradictions, and creates a coherent narrative.
    
    Args:
        findings: List of research findings, each containing:
            - content: The finding text
            - source: Source URL or reference
            - credibility_score: Optional credibility score (0.0-1.0)
            - type: Optional type (fact, opinion, statistic, quote)
            - date: Optional publication date
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
        
    Example:
        >>> findings = [
        ...     {"content": "Climate change is accelerating", "source": "nature.com", "credibility_score": 0.9, "type": "fact"},
        ...     {"content": "Global temperatures rising", "source": "science.org", "credibility_score": 0.9, "type": "statistic"}
        ... ]
        >>> result = compile_research(findings, "Climate Change Trends", "standard")
        >>> print(result["confidence_level"])
        "high"
    """
    try:
        # Validate inputs
        if not isinstance(findings, list):
            return {
                "status": "error",
                "message": "findings must be a list"
            }
        
        validation_error = validate_string_not_empty(topic, "topic")
        if validation_error:
            return validation_error
        
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
                "status": "success",
                "compiled_at": datetime.now().isoformat()
            }
        
        logger.info(f"Compiling research on '{topic}' with {len(findings)} findings (structure={structure})")
        
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
            compilation = _build_comparative_compilation(
                findings, facts, opinions, statistics
            )
        elif structure == "chronological":
            compilation = _build_chronological_compilation(findings)
        elif structure == "thematic":
            compilation = _build_thematic_compilation(findings)
        else:  # standard
            compilation = _build_standard_compilation(
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
            "status": "success",
            "compiled_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error compiling research: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to compile research: {str(e)}",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }


# Helper functions for different compilation structures

def _build_standard_compilation(
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
