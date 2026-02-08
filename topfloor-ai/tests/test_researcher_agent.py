"""
Tests for Researcher Agent
"""

import pytest
from app.agents.researcher import ResearcherAgent
from app.agents.registry import AgentRegistry, AgentType
from google.adk.tools import google_search


def test_researcher_agent_has_google_search_tool():
    """Test that Researcher Agent includes google_search tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that google_search is in the tools list
    assert google_search in tools, \
        f"google_search tool not found in tools"


def test_researcher_agent_has_save_research_document_tool():
    """Test that Researcher Agent includes save_research_document tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that save_research_document is in the tools list
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    assert any('save_research_document' in name.lower() for name in tool_names), \
        f"save_research_document tool not found in tools: {tool_names}"


def test_researcher_agent_has_extract_key_findings_tool():
    """Test that Researcher Agent includes extract_key_findings tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that extract_key_findings is in the tools list
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    assert any('extract_key_findings' in name.lower() for name in tool_names), \
        f"extract_key_findings tool not found in tools: {tool_names}"


def test_researcher_agent_has_fetch_content_tool():
    """Test that Researcher Agent includes fetch_content_tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that fetch_content_tool is in the tools list
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    assert any('fetch_content' in name.lower() for name in tool_names), \
        f"fetch_content_tool not found in tools: {tool_names}"


def test_researcher_agent_tools_count():
    """Test that Researcher Agent has the expected number of tools"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Should have 6 tools: google_search, fetch_content_tool, save_research_document, extract_key_findings, verify_source, compile_research
    assert len(tools) == 6, f"Expected 6 tools, got {len(tools)}"


def test_researcher_agent_has_verify_source_tool():
    """Test that Researcher Agent includes verify_source tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that verify_source is in the tools list
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    assert any('verify_source' in name.lower() for name in tool_names), \
        f"verify_source tool not found in tools: {tool_names}"


def test_verify_source_credible_https_domain():
    """Test verify_source with a credible HTTPS domain"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Test with a credible source
    result = verify_source_tool.func("https://www.nytimes.com/article")
    
    assert result["url"] == "https://www.nytimes.com/article"
    assert result["domain"] == "nytimes.com"
    assert result["has_ssl"] is True
    assert result["tld"] == "com"
    assert result["credibility_score"] >= 0.6
    assert result["is_credible"] is True
    assert len(result["warnings"]) == 0


def test_verify_source_non_https_domain():
    """Test verify_source with a non-HTTPS domain"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Test with a non-HTTPS source
    result = verify_source_tool.func("http://example.com/article")
    
    assert result["url"] == "http://example.com/article"
    assert result["has_ssl"] is False
    assert result["is_credible"] is False
    assert any("HTTPS" in warning for warning in result["warnings"])


def test_verify_source_gov_domain():
    """Test verify_source with a government domain"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Test with a .gov domain
    result = verify_source_tool.func("https://www.cdc.gov/health")
    
    assert result["domain"] == "cdc.gov"
    assert result["has_ssl"] is True
    assert result["tld"] == "gov"
    assert result["credibility_score"] >= 0.8
    assert result["is_credible"] is True


def test_verify_source_suspicious_tld():
    """Test verify_source with a suspicious TLD"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Test with a suspicious TLD
    result = verify_source_tool.func("https://example.xyz/article")
    
    assert result["tld"] == "xyz"
    assert any("Suspicious TLD" in warning for warning in result["warnings"])
    assert result["credibility_score"] < 0.6


def test_verify_source_invalid_url():
    """Test verify_source with an invalid URL"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Test with an invalid URL
    result = verify_source_tool.func("not-a-valid-url")
    
    assert result["credibility_score"] <= 0.5
    assert result["is_credible"] is False



def test_researcher_agent_has_compile_research_tool():
    """Test that Researcher Agent includes compile_research tool"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Check that compile_research is in the tools list
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    assert any('compile_research' in name.lower() for name in tool_names), \
        f"compile_research tool not found in tools: {tool_names}"


def test_compile_research_with_empty_findings():
    """Test compile_research with no findings"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Test with empty findings
    result = compile_research_tool.func([], "Test Topic")
    
    assert result["topic"] == "Test Topic"
    assert result["confidence_level"] == "low"
    assert len(result["key_findings"]) == 0
    assert result["source_analysis"]["total_sources"] == 0


def test_compile_research_with_credible_findings():
    """Test compile_research with credible findings"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Test with credible findings
    findings = [
        {
            "content": "Climate change is accelerating",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact"
        },
        {
            "content": "Global temperatures rising by 1.5C",
            "source": "https://www.science.org/article2",
            "credibility_score": 0.85,
            "type": "statistic"
        },
        {
            "content": "Renewable energy adoption increasing",
            "source": "https://www.reuters.com/article3",
            "credibility_score": 0.8,
            "type": "fact"
        }
    ]
    
    result = compile_research_tool.func(findings, "Climate Change Research")
    
    assert result["topic"] == "Climate Change Research"
    assert result["confidence_level"] == "high"
    assert result["source_analysis"]["total_sources"] == 3
    assert result["source_analysis"]["credible_sources"] == 3
    assert len(result["key_findings"]) == 3
    assert len(result["sources_cited"]) == 3


def test_compile_research_with_mixed_credibility():
    """Test compile_research with mixed credibility findings"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Test with mixed credibility
    findings = [
        {
            "content": "High credibility finding",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact"
        },
        {
            "content": "Low credibility finding",
            "source": "http://example.xyz/article2",
            "credibility_score": 0.3,
            "type": "opinion"
        }
    ]
    
    result = compile_research_tool.func(findings, "Mixed Research")
    
    assert result["topic"] == "Mixed Research"
    assert result["confidence_level"] == "medium"
    assert result["source_analysis"]["total_sources"] == 2
    assert result["source_analysis"]["credible_sources"] == 1


def test_compile_research_detects_contradictions():
    """Test compile_research detects contradictory findings"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Test with contradictory findings (using exact keywords from opposing_pairs)
    findings = [
        {
            "content": "Sales increase rapidly",
            "source": "https://www.forbes.com/article1",
            "credibility_score": 0.8,
            "type": "fact"
        },
        {
            "content": "Sales decrease significantly",
            "source": "https://www.bloomberg.com/article2",
            "credibility_score": 0.8,
            "type": "fact"
        }
    ]
    
    result = compile_research_tool.func(findings, "Sales Analysis")
    
    assert result["topic"] == "Sales Analysis"
    assert len(result["contradictions"]) > 0


def test_compile_research_standard_structure():
    """Test compile_research with standard structure"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    findings = [
        {
            "content": "Fact finding",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact"
        }
    ]
    
    result = compile_research_tool.func(findings, "Test Topic", "standard")
    
    assert "Research Compilation" in result["compilation"]
    assert "Factual Findings" in result["compilation"]


def test_compile_research_comparative_structure():
    """Test compile_research with comparative structure"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    findings = [
        {
            "content": "This is a positive finding with support",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact"
        },
        {
            "content": "This is a negative finding with opposition",
            "source": "https://www.science.org/article2",
            "credibility_score": 0.9,
            "type": "fact"
        }
    ]
    
    result = compile_research_tool.func(findings, "Test Topic", "comparative")
    
    assert "Comparative Analysis" in result["compilation"]
    assert "Supporting Evidence" in result["compilation"]
    assert "Opposing Evidence" in result["compilation"]


def test_compile_research_provides_recommendations():
    """Test compile_research provides recommendations"""
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find the compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Test with low credibility findings
    findings = [
        {
            "content": "Low credibility finding",
            "source": "http://example.com/article",
            "credibility_score": 0.3,
            "type": "opinion"
        }
    ]
    
    result = compile_research_tool.func(findings, "Test Topic")
    
    assert len(result["recommendations"]) > 0
    assert result["confidence_level"] == "low"
