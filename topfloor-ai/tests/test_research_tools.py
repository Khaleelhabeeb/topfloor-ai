"""
Tests for Research Tools
"""

import pytest
from unittest.mock import Mock, patch
from app.tools.research_tools import (
    web_search, 
    validate_string_not_empty,
    fetch_content,
    _extract_text_content,
    _extract_structured_content,
    _extract_metadata
)
from bs4 import BeautifulSoup


def test_web_search_basic():
    """Test web_search with basic query"""
    result = web_search("climate change research")
    
    assert result["status"] == "success"
    assert result["original_query"] == "climate change research"
    assert result["query"] == "climate change research"
    assert result["num_results"] == 10
    assert "timestamp" in result
    assert "integration" in result


def test_web_search_with_num_results():
    """Test web_search with custom num_results"""
    result = web_search("artificial intelligence", num_results=5)
    
    assert result["status"] == "success"
    assert result["num_results"] == 5


def test_web_search_caps_num_results():
    """Test web_search caps num_results at 50"""
    result = web_search("machine learning", num_results=100)
    
    assert result["status"] == "success"
    assert result["num_results"] == 50


def test_web_search_with_site_filter():
    """Test web_search with site filter"""
    result = web_search(
        "python programming",
        filters={"site": "stackoverflow.com"}
    )
    
    assert result["status"] == "success"
    assert "site:stackoverflow.com" in result["query"]
    assert result["filters"]["site"] == "stackoverflow.com"


def test_web_search_with_filetype_filter():
    """Test web_search with filetype filter"""
    result = web_search(
        "research paper",
        filters={"filetype": "pdf"}
    )
    
    assert result["status"] == "success"
    assert "filetype:pdf" in result["query"]
    assert result["filters"]["filetype"] == "pdf"


def test_web_search_with_multiple_filters():
    """Test web_search with multiple filters"""
    result = web_search(
        "academic research",
        filters={
            "site": "arxiv.org",
            "filetype": "pdf",
            "date_range": "year"
        }
    )
    
    assert result["status"] == "success"
    assert "site:arxiv.org" in result["query"]
    assert "filetype:pdf" in result["query"]
    assert result["filters"]["date_range"] == "year"


def test_web_search_empty_query():
    """Test web_search with empty query"""
    result = web_search("")
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_web_search_invalid_num_results():
    """Test web_search with invalid num_results"""
    result = web_search("test query", num_results=-5)
    
    assert result["status"] == "error"
    assert "positive integer" in result["message"]


def test_web_search_zero_num_results():
    """Test web_search with zero num_results"""
    result = web_search("test query", num_results=0)
    
    assert result["status"] == "error"
    assert "positive integer" in result["message"]


def test_web_search_non_integer_num_results():
    """Test web_search with non-integer num_results"""
    result = web_search("test query", num_results="ten")
    
    assert result["status"] == "error"
    assert "positive integer" in result["message"]


def test_web_search_whitespace_query():
    """Test web_search with whitespace-only query"""
    result = web_search("   ")
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_web_search_none_query():
    """Test web_search with None query"""
    result = web_search(None)
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_validate_string_not_empty_valid():
    """Test validate_string_not_empty with valid string"""
    result = validate_string_not_empty("valid string", "test_field")
    
    assert result is None


def test_validate_string_not_empty_empty():
    """Test validate_string_not_empty with empty string"""
    result = validate_string_not_empty("", "test_field")
    
    assert result is not None
    assert result["status"] == "error"
    assert "test_field" in result["message"]


def test_validate_string_not_empty_whitespace():
    """Test validate_string_not_empty with whitespace"""
    result = validate_string_not_empty("   ", "test_field")
    
    assert result is not None
    assert result["status"] == "error"


def test_validate_string_not_empty_none():
    """Test validate_string_not_empty with None"""
    result = validate_string_not_empty(None, "test_field")
    
    assert result is not None
    assert result["status"] == "error"


def test_validate_string_not_empty_non_string():
    """Test validate_string_not_empty with non-string"""
    result = validate_string_not_empty(123, "test_field")
    
    assert result is not None
    assert result["status"] == "error"


def test_web_search_returns_integration_info():
    """Test that web_search returns integration information"""
    result = web_search("test query")
    
    assert result["status"] == "success"
    assert "google_search" in result["integration"]
    assert "google.adk.tools" in result["integration"]


def test_web_search_returns_note():
    """Test that web_search returns explanatory note"""
    result = web_search("test query")
    
    assert result["status"] == "success"
    assert "note" in result
    assert "Researcher Agent" in result["note"]
    assert "google_search" in result["note"]



# Tests for fetch_content

def test_fetch_content_empty_url():
    """Test fetch_content with empty URL"""
    result = fetch_content("")
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_fetch_content_invalid_url():
    """Test fetch_content with invalid URL format"""
    result = fetch_content("not-a-valid-url")
    
    assert result["status"] == "error"
    assert "invalid url" in result["message"].lower()


def test_fetch_content_invalid_extract_type():
    """Test fetch_content with invalid extract_type"""
    result = fetch_content("https://example.com", extract_type="invalid")
    
    assert result["status"] == "error"
    assert "invalid extract_type" in result["message"].lower()


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_text_extraction(mock_client):
    """Test fetch_content with text extraction"""
    # Mock HTML response
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a test paragraph with enough content to be included.</p>
            <p>Another paragraph with sufficient length for testing purposes.</p>
        </body>
    </html>
    """
    
    mock_response = Mock()
    mock_response.text = html_content
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.raise_for_status = Mock()
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(return_value=mock_response)
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com", extract_type="text")
    
    assert result["status"] == "success"
    assert result["url"] == "https://example.com"
    assert result["extract_type"] == "text"
    assert "content" in result
    assert "title" in result["content"]
    assert result["content"]["title"] == "Test Page"
    assert "paragraphs" in result["content"]
    assert len(result["content"]["paragraphs"]) == 2


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_structured_extraction(mock_client):
    """Test fetch_content with structured extraction"""
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading</h2>
            <p>Test paragraph with sufficient content for extraction.</p>
            <a href="https://example.com/link">Test Link</a>
            <img src="image.jpg" alt="Test Image">
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
    </html>
    """
    
    mock_response = Mock()
    mock_response.text = html_content
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.raise_for_status = Mock()
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(return_value=mock_response)
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com", extract_type="structured")
    
    assert result["status"] == "success"
    assert "content" in result
    assert "title" in result["content"]
    assert "headings" in result["content"]
    assert "paragraphs" in result["content"]
    assert "links" in result["content"]
    assert "images" in result["content"]
    assert "lists" in result["content"]
    assert len(result["content"]["headings"]) >= 2
    assert len(result["content"]["links"]) >= 1
    assert len(result["content"]["images"]) >= 1


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_metadata_extraction(mock_client):
    """Test fetch_content with metadata extraction"""
    html_content = """
    <html lang="en">
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="author" content="Test Author">
            <meta name="keywords" content="test, keywords">
            <meta property="og:title" content="OG Title">
            <link rel="canonical" href="https://example.com/canonical">
        </head>
        <body>
            <h1>Content</h1>
        </body>
    </html>
    """
    
    mock_response = Mock()
    mock_response.text = html_content
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.raise_for_status = Mock()
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(return_value=mock_response)
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com", extract_type="metadata")
    
    assert result["status"] == "success"
    assert "content" in result
    assert result["content"]["title"] == "Test Page"
    assert result["content"]["language"] == "en"
    assert "meta_tags" in result["content"]
    assert result["content"]["meta_tags"]["description"] == "Test description"
    assert result["content"]["meta_tags"]["author"] == "Test Author"


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_full_extraction(mock_client):
    """Test fetch_content with full extraction"""
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>Test paragraph with enough content to be extracted properly.</p>
        </body>
    </html>
    """
    
    mock_response = Mock()
    mock_response.text = html_content
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.raise_for_status = Mock()
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(return_value=mock_response)
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com", extract_type="full")
    
    assert result["status"] == "success"
    assert "content" in result
    assert "text" in result["content"]
    assert "structured" in result["content"]
    assert "metadata" in result["content"]


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_http_error(mock_client):
    """Test fetch_content with HTTP error"""
    import httpx
    
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.reason_phrase = "Not Found"
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(side_effect=httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response
    ))
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com/notfound")
    
    assert result["status"] == "error"
    assert "404" in result["message"]


@patch('app.tools.research_tools.httpx.Client')
def test_fetch_content_timeout(mock_client):
    """Test fetch_content with timeout"""
    import httpx
    
    mock_client_instance = Mock()
    mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
    mock_client_instance.__exit__ = Mock(return_value=False)
    mock_client_instance.get = Mock(side_effect=httpx.TimeoutException("Timeout"))
    mock_client.return_value = mock_client_instance
    
    result = fetch_content("https://example.com")
    
    assert result["status"] == "error"
    assert "timeout" in result["message"].lower()


def test_extract_text_content():
    """Test _extract_text_content helper function"""
    html = """
    <html>
        <head><title>Test Title</title></head>
        <body>
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <p>This is a paragraph with enough content to be included in extraction.</p>
            <p>Another paragraph with sufficient length for testing purposes here.</p>
            <script>console.log('should be removed');</script>
            <style>.test { color: red; }</style>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'lxml')
    result = _extract_text_content(soup)
    
    assert result["title"] == "Test Title"
    assert len(result["paragraphs"]) == 2
    assert len(result["headings"]) == 2
    assert result["headings"][0]["level"] == "h1"
    assert result["headings"][0]["text"] == "Heading 1"
    assert "console.log" not in result["full_text"]
    assert "color: red" not in result["full_text"]


def test_extract_structured_content():
    """Test _extract_structured_content helper function"""
    html = """
    <html>
        <head><title>Test Title</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>Test paragraph with enough content for extraction purposes.</p>
            <a href="https://example.com">External Link</a>
            <a href="/internal">Internal Link</a>
            <img src="image.jpg" alt="Test Image" title="Image Title">
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'lxml')
    result = _extract_structured_content(soup)
    
    assert result["title"] == "Test Title"
    assert result["main_heading"] == "Main Heading"
    assert len(result["headings"]) >= 1
    assert len(result["paragraphs"]) >= 1
    assert len(result["links"]) == 2
    assert result["links"][0]["is_external"] == True
    assert result["links"][1]["is_external"] == False
    assert len(result["images"]) == 1
    assert result["images"][0]["alt"] == "Test Image"
    assert len(result["lists"]) == 1
    assert result["lists"][0]["type"] == "ul"


def test_extract_metadata():
    """Test _extract_metadata helper function"""
    html = """
    <html lang="en">
        <head>
            <title>Test Title</title>
            <meta name="description" content="Test description">
            <meta name="author" content="John Doe">
            <meta name="keywords" content="test, metadata, extraction">
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta name="twitter:card" content="summary">
            <link rel="canonical" href="https://example.com/canonical">
        </head>
        <body></body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'lxml')
    result = _extract_metadata(soup, "https://example.com/test")
    
    assert result["url"] == "https://example.com/test"
    assert result["domain"] == "example.com"
    assert result["title"] == "Test Title"
    assert result["language"] == "en"
    assert result["canonical_url"] == "https://example.com/canonical"
    assert result["meta_tags"]["description"] == "Test description"
    assert result["meta_tags"]["author"] == "John Doe"
    assert result["meta_tags"]["keywords"] == "test, metadata, extraction"
    assert "open_graph" in result["meta_tags"]
    assert result["meta_tags"]["open_graph"]["title"] == "OG Title"
    assert "twitter_card" in result["meta_tags"]
    assert result["meta_tags"]["twitter_card"]["card"] == "summary"


# Tests for verify_source

def test_verify_source_credible_https_domain():
    """Test verify_source with credible HTTPS domain"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.nytimes.com/article")
    
    assert result["status"] == "success"
    assert result["url"] == "https://www.nytimes.com/article"
    assert result["domain"] == "nytimes.com"
    assert result["has_ssl"] == True
    assert result["tld"] == "com"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.6
    assert "ssl" in result["checks_performed"]
    assert "domain_reputation" in result["checks_performed"]


def test_verify_source_credible_gov_domain():
    """Test verify_source with government domain"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.cdc.gov/health")
    
    assert result["status"] == "success"
    assert result["domain"] == "cdc.gov"
    assert result["has_ssl"] == True
    assert result["tld"] == "gov"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.6


def test_verify_source_credible_edu_domain():
    """Test verify_source with educational domain"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.stanford.edu/research")
    
    assert result["status"] == "success"
    assert result["domain"] == "stanford.edu"
    assert result["has_ssl"] == True
    assert result["tld"] == "edu"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.6


def test_verify_source_no_ssl():
    """Test verify_source with HTTP (no SSL)"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("http://example.com/article")
    
    assert result["status"] == "success"
    assert result["has_ssl"] == False
    assert result["is_credible"] == False  # No SSL means not credible
    assert any("HTTPS" in warning for warning in result["warnings"])


def test_verify_source_suspicious_tld():
    """Test verify_source with suspicious TLD"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://example.xyz/article")
    
    assert result["status"] == "success"
    assert result["tld"] == "xyz"
    assert any("Suspicious TLD" in warning for warning in result["warnings"])
    assert result["credibility_score"] < 0.6


def test_verify_source_suspicious_patterns():
    """Test verify_source with suspicious domain patterns"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://free-download-click.com/article")
    
    assert result["status"] == "success"
    assert any("suspicious" in warning.lower() for warning in result["warnings"])
    # Score should be reduced due to suspicious patterns
    assert result["credibility_score"] <= 0.6


def test_verify_source_academic_domain():
    """Test verify_source with academic domain"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.nature.com/articles/science")
    
    assert result["status"] == "success"
    assert result["domain"] == "nature.com"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.6


def test_verify_source_news_organization():
    """Test verify_source with known news organization"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.bbc.com/news/article")
    
    assert result["status"] == "success"
    assert result["domain"] == "bbc.com"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.6


def test_verify_source_empty_url():
    """Test verify_source with empty URL"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("")
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_verify_source_none_url():
    """Test verify_source with None URL"""
    from app.tools.research_tools import verify_source
    
    result = verify_source(None)
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_verify_source_whitespace_url():
    """Test verify_source with whitespace-only URL"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("   ")
    
    assert result["status"] == "error"
    assert "required" in result["message"].lower()


def test_verify_source_removes_www():
    """Test verify_source removes www prefix from domain"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.example.com/page")
    
    assert result["status"] == "success"
    assert result["domain"] == "example.com"
    assert not result["domain"].startswith("www.")


def test_verify_source_checks_performed():
    """Test verify_source includes all checks performed"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://example.com/page")
    
    assert result["status"] == "success"
    assert "checks_performed" in result
    assert "ssl" in result["checks_performed"]
    assert "domain_reputation" in result["checks_performed"]
    assert "tld" in result["checks_performed"]
    assert "domain_structure" in result["checks_performed"]
    assert "suspicious_patterns" in result["checks_performed"]


def test_verify_source_recommendation():
    """Test verify_source includes recommendation"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.nytimes.com/article")
    
    assert result["status"] == "success"
    assert "recommendation" in result
    assert isinstance(result["recommendation"], str)


def test_verify_source_timestamp():
    """Test verify_source includes timestamp"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://example.com/page")
    
    assert result["status"] == "success"
    assert "timestamp" in result


def test_verify_source_credibility_score_range():
    """Test verify_source credibility score is between 0 and 1"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://example.com/page")
    
    assert result["status"] == "success"
    assert 0.0 <= result["credibility_score"] <= 1.0


def test_verify_source_multiple_credible_indicators():
    """Test verify_source with multiple credible indicators"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.nih.gov/research")
    
    assert result["status"] == "success"
    assert result["has_ssl"] == True
    assert result["tld"] == "gov"
    assert result["is_credible"] == True
    assert result["credibility_score"] >= 0.8  # Should have high score


def test_verify_source_reuters():
    """Test verify_source with Reuters"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.reuters.com/article")
    
    assert result["status"] == "success"
    assert result["domain"] == "reuters.com"
    assert result["is_credible"] == True


def test_verify_source_arxiv():
    """Test verify_source with arXiv"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://arxiv.org/abs/1234.5678")
    
    assert result["status"] == "success"
    assert result["domain"] == "arxiv.org"
    assert result["is_credible"] == True


def test_verify_source_who():
    """Test verify_source with WHO"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://www.who.int/health")
    
    assert result["status"] == "success"
    assert result["domain"] == "who.int"
    assert result["is_credible"] == True


def test_verify_source_with_criteria():
    """Test verify_source with specific criteria"""
    from app.tools.research_tools import verify_source
    
    result = verify_source("https://example.com/page", criteria=["ssl", "domain"])
    
    assert result["status"] == "success"
    # Criteria parameter is optional and doesn't affect current implementation
    assert "checks_performed" in result


def test_verify_source_invalid_domain_structure():
    """Test verify_source with invalid domain structure"""
    from app.tools.research_tools import verify_source
    
    # This should still parse but may have warnings
    result = verify_source("https://nodomain")
    
    assert result["status"] == "success"
    # May have warnings about domain structure


def test_verify_source_error_handling():
    """Test verify_source handles exceptions gracefully"""
    from app.tools.research_tools import verify_source
    
    # Test with a malformed URL that might cause parsing issues
    result = verify_source("https://")
    
    # Should return error or handle gracefully
    assert "status" in result
    assert result["status"] in ["success", "error"]
