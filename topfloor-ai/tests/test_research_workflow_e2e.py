"""
End-to-end tests for Researcher Agent workflow
Tests the complete research workflow from search to compilation
"""

import pytest
from app.agents.researcher import ResearcherAgent
from app.agents.registry import AgentRegistry, AgentType


def test_research_workflow_complete():
    """
    Test complete research workflow end-to-end:
    1. Initialize Researcher Agent
    2. Verify all tools are available
    3. Execute verify_source tool
    4. Execute compile_research tool
    5. Verify research document structure
    """
    # Step 1: Initialize Researcher Agent
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Step 2: Verify all required tools are available
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
    
    required_tools = [
        'google_search',
        'save_research_document',
        'extract_key_findings',
        'verify_source',
        'compile_research'
    ]
    
    for required_tool in required_tools:
        assert any(required_tool in name.lower() for name in tool_names), \
            f"Required tool '{required_tool}' not found in tools"
    
    # Step 3: Find and execute verify_source tool
    verify_source_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'verify_source' in tool.name.lower():
            verify_source_tool = tool
            break
    
    assert verify_source_tool is not None, "verify_source tool not found"
    
    # Verify multiple sources with different credibility levels
    sources = [
        "https://www.nature.com/articles/climate-change",
        "https://www.science.org/research/data",
        "https://www.bbc.com/news/article"
    ]
    
    verified_sources = []
    for source in sources:
        result = verify_source_tool.func(source)
        verified_sources.append(result)
        
        # Verify result structure
        assert "url" in result
        assert "domain" in result
        assert "has_ssl" in result
        assert "credibility_score" in result
        assert "is_credible" in result
        assert "warnings" in result
    
    # Step 4: Find and execute compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None, "compile_research tool not found"
    
    # Create research findings based on verified sources
    findings = [
        {
            "content": "Climate change is accelerating at unprecedented rates",
            "source": sources[0],
            "credibility_score": verified_sources[0]["credibility_score"],
            "type": "fact"
        },
        {
            "content": "Global temperatures have risen by 1.5°C since pre-industrial times",
            "source": sources[1],
            "credibility_score": verified_sources[1]["credibility_score"],
            "type": "statistic"
        },
        {
            "content": "Renewable energy adoption is increasing worldwide",
            "source": sources[2],
            "credibility_score": verified_sources[2]["credibility_score"],
            "type": "fact"
        }
    ]
    
    # Compile research
    compilation = compile_research_tool.func(
        findings=findings,
        topic="Climate Change Research",
        structure="standard"
    )
    
    # Step 5: Verify research document structure
    assert "topic" in compilation
    assert compilation["topic"] == "Climate Change Research"
    
    assert "compilation" in compilation
    assert len(compilation["compilation"]) > 0
    assert "Research Compilation" in compilation["compilation"]
    
    assert "executive_summary" in compilation
    assert len(compilation["executive_summary"]) > 0
    
    assert "key_findings" in compilation
    assert len(compilation["key_findings"]) > 0
    
    assert "source_analysis" in compilation
    assert compilation["source_analysis"]["total_sources"] == 3
    
    assert "confidence_level" in compilation
    assert compilation["confidence_level"] in ["low", "medium", "high"]
    
    assert "recommendations" in compilation
    assert isinstance(compilation["recommendations"], list)
    
    assert "sources_cited" in compilation
    assert len(compilation["sources_cited"]) == 3
    
    assert "compiled_at" in compilation


def test_research_workflow_with_source_verification():
    """
    Test research workflow with emphasis on source verification:
    1. Verify multiple sources with different credibility
    2. Compile research with mixed credibility sources
    3. Verify confidence level reflects source quality
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find tools
    verify_source_tool = None
    compile_research_tool = None
    
    for tool in tools:
        if hasattr(tool, 'name'):
            if 'verify_source' in tool.name.lower():
                verify_source_tool = tool
            elif 'compile_research' in tool.name.lower():
                compile_research_tool = tool
    
    assert verify_source_tool is not None
    assert compile_research_tool is not None
    
    # Test with high credibility sources
    high_credibility_sources = [
        "https://www.nature.com/article1",
        "https://www.science.org/article2",
        "https://www.cdc.gov/health"
    ]
    
    findings_high = []
    for source in high_credibility_sources:
        verification = verify_source_tool.func(source)
        findings_high.append({
            "content": f"Finding from {verification['domain']}",
            "source": source,
            "credibility_score": verification["credibility_score"],
            "type": "fact"
        })
    
    compilation_high = compile_research_tool.func(
        findings=findings_high,
        topic="High Credibility Research"
    )
    
    # Should have high confidence with credible sources
    assert compilation_high["confidence_level"] in ["medium", "high"]
    assert compilation_high["source_analysis"]["credible_sources"] >= 2
    
    # Test with low credibility sources
    low_credibility_sources = [
        "http://example.xyz/article",
        "http://random-site.com/info"
    ]
    
    findings_low = []
    for source in low_credibility_sources:
        verification = verify_source_tool.func(source)
        findings_low.append({
            "content": f"Finding from {verification['domain']}",
            "source": source,
            "credibility_score": verification["credibility_score"],
            "type": "opinion"
        })
    
    compilation_low = compile_research_tool.func(
        findings=findings_low,
        topic="Low Credibility Research"
    )
    
    # Should have low confidence with non-credible sources
    assert compilation_low["confidence_level"] == "low"
    assert len(compilation_low["recommendations"]) > 0


def test_research_workflow_with_contradictions():
    """
    Test research workflow with contradictory findings:
    1. Create findings with opposing viewpoints
    2. Compile research
    3. Verify contradictions are detected
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None
    
    # Create contradictory findings
    findings = [
        {
            "content": "Sales increase significantly in Q4",
            "source": "https://www.forbes.com/article1",
            "credibility_score": 0.8,
            "type": "fact"
        },
        {
            "content": "Sales decrease dramatically in Q4",
            "source": "https://www.bloomberg.com/article2",
            "credibility_score": 0.8,
            "type": "fact"
        },
        {
            "content": "Market shows positive growth trends",
            "source": "https://www.reuters.com/article3",
            "credibility_score": 0.8,
            "type": "fact"
        },
        {
            "content": "Market shows negative growth trends",
            "source": "https://www.wsj.com/article4",
            "credibility_score": 0.8,
            "type": "fact"
        }
    ]
    
    compilation = compile_research_tool.func(
        findings=findings,
        topic="Market Analysis with Contradictions"
    )
    
    # Verify contradictions are detected
    assert "contradictions" in compilation
    assert len(compilation["contradictions"]) > 0
    
    # Verify recommendations include investigating contradictions
    assert any(
        "contradiction" in rec.lower() 
        for rec in compilation["recommendations"]
    )


def test_research_workflow_different_structures():
    """
    Test research workflow with different compilation structures:
    1. Standard structure
    2. Comparative structure
    3. Chronological structure
    4. Thematic structure
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None
    
    # Create sample findings
    findings = [
        {
            "content": "Positive finding with support",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact",
            "date": "2026-01-15"
        },
        {
            "content": "Negative finding with opposition",
            "source": "https://www.science.org/article2",
            "credibility_score": 0.9,
            "type": "opinion",
            "date": "2026-01-20"
        },
        {
            "content": "Statistical data point",
            "source": "https://www.cdc.gov/data",
            "credibility_score": 0.95,
            "type": "statistic",
            "date": "2026-01-25"
        }
    ]
    
    # Test standard structure
    standard = compile_research_tool.func(
        findings=findings,
        topic="Test Topic",
        structure="standard"
    )
    assert "Research Compilation" in standard["compilation"]
    assert "Factual Findings" in standard["compilation"]
    
    # Test comparative structure
    comparative = compile_research_tool.func(
        findings=findings,
        topic="Test Topic",
        structure="comparative"
    )
    assert "Comparative Analysis" in comparative["compilation"]
    assert "Supporting Evidence" in comparative["compilation"]
    assert "Opposing Evidence" in comparative["compilation"]
    
    # Test chronological structure
    chronological = compile_research_tool.func(
        findings=findings,
        topic="Test Topic",
        structure="chronological"
    )
    assert "Chronological Research Timeline" in chronological["compilation"]
    assert "Timeline of Findings" in chronological["compilation"]
    
    # Test thematic structure
    thematic = compile_research_tool.func(
        findings=findings,
        topic="Test Topic",
        structure="thematic"
    )
    assert "Thematic Research Compilation" in thematic["compilation"]


def test_research_workflow_save_document():
    """
    Test research workflow with document saving:
    1. Compile research
    2. Save research document
    3. Verify document metadata
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find tools
    compile_research_tool = None
    save_document_tool = None
    
    for tool in tools:
        if hasattr(tool, 'name'):
            if 'compile_research' in tool.name.lower():
                compile_research_tool = tool
            elif 'save_research_document' in tool.name.lower():
                save_document_tool = tool
    
    assert compile_research_tool is not None
    assert save_document_tool is not None
    
    # Create and compile research
    findings = [
        {
            "content": "Research finding 1",
            "source": "https://www.nature.com/article1",
            "credibility_score": 0.9,
            "type": "fact"
        }
    ]
    
    compilation = compile_research_tool.func(
        findings=findings,
        topic="Test Research"
    )
    
    # Save document
    sources = [f["source"] for f in findings]
    save_result = save_document_tool.func(
        title="Test Research Document",
        content=compilation["compilation"],
        sources=sources,
        tags=["test", "research"]
    )
    
    # Verify save result
    assert "status" in save_result
    assert save_result["status"] == "saved"
    assert "document_id" in save_result
    assert "title" in save_result
    assert save_result["title"] == "Test Research Document"
    assert "source_count" in save_result
    assert save_result["source_count"] == len(sources)


def test_research_workflow_extract_key_findings():
    """
    Test research workflow with key findings extraction:
    1. Create research content
    2. Extract key findings
    3. Verify extracted findings
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find extract_key_findings tool
    extract_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'extract_key_findings' in tool.name.lower():
            extract_tool = tool
            break
    
    assert extract_tool is not None
    
    # Create research content with bullet points
    content = """
    # Research Summary
    
    Key findings from the research:
    - Finding 1: Climate change is accelerating
    - Finding 2: Renewable energy adoption increasing
    - Finding 3: Carbon emissions need to be reduced
    * Finding 4: Policy changes are necessary
    * Finding 5: Technology innovation is critical
    """
    
    # Extract findings
    findings = extract_tool.func(content, num_findings=3)
    
    # Verify extraction
    assert isinstance(findings, list)
    assert len(findings) <= 3
    assert all(isinstance(f, str) for f in findings)


def test_research_workflow_empty_findings():
    """
    Test research workflow with empty findings:
    1. Attempt to compile with no findings
    2. Verify graceful handling
    3. Verify appropriate recommendations
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Find compile_research tool
    compile_research_tool = None
    for tool in tools:
        if hasattr(tool, 'name') and 'compile_research' in tool.name.lower():
            compile_research_tool = tool
            break
    
    assert compile_research_tool is not None
    
    # Compile with empty findings
    compilation = compile_research_tool.func(
        findings=[],
        topic="Empty Research"
    )
    
    # Verify graceful handling
    assert compilation["topic"] == "Empty Research"
    assert compilation["confidence_level"] == "low"
    assert len(compilation["key_findings"]) == 0
    assert compilation["source_analysis"]["total_sources"] == 0
    assert len(compilation["recommendations"]) > 0
    assert any(
        "gather" in rec.lower() or "research" in rec.lower()
        for rec in compilation["recommendations"]
    )


def test_research_workflow_integration():
    """
    Full integration test simulating a real research workflow:
    1. Verify multiple sources
    2. Create findings from verified sources
    3. Compile research with standard structure
    4. Extract key findings from compilation
    5. Save research document
    """
    definition = AgentRegistry.get_agent(AgentType.RESEARCHER)
    researcher = ResearcherAgent(definition)
    tools = researcher.build_tools()
    
    # Get all tools
    tool_map = {}
    for tool in tools:
        if hasattr(tool, 'name'):
            tool_map[tool.name] = tool
    
    # Step 1: Verify sources
    sources_to_verify = [
        "https://www.nature.com/climate-research",
        "https://www.science.org/environmental-data",
        "https://www.bbc.com/news/climate"
    ]
    
    verified_results = []
    for source in sources_to_verify:
        result = tool_map['verify_source'].func(source)
        verified_results.append(result)
    
    # Step 2: Create findings
    findings = []
    for i, (source, verification) in enumerate(zip(sources_to_verify, verified_results)):
        findings.append({
            "content": f"Research finding {i+1} about climate change",
            "source": source,
            "credibility_score": verification["credibility_score"],
            "type": "fact" if i % 2 == 0 else "statistic"
        })
    
    # Step 3: Compile research
    compilation = tool_map['compile_research'].func(
        findings=findings,
        topic="Climate Change Comprehensive Study",
        structure="standard"
    )
    
    # Verify compilation
    assert compilation["topic"] == "Climate Change Comprehensive Study"
    assert len(compilation["key_findings"]) > 0
    assert compilation["source_analysis"]["total_sources"] == 3
    
    # Step 4: Extract key findings
    extracted = tool_map['extract_key_findings'].func(
        compilation["compilation"],
        num_findings=5
    )
    
    assert isinstance(extracted, list)
    
    # Step 5: Save document
    save_result = tool_map['save_research_document'].func(
        title="Climate Change Comprehensive Study",
        content=compilation["compilation"],
        sources=sources_to_verify,
        tags=["climate", "environment", "research"]
    )
    
    assert save_result["status"] == "saved"
    assert save_result["source_count"] == 3
    
    # Verify complete workflow success
    assert compilation["confidence_level"] in ["medium", "high"]
    assert len(compilation["sources_cited"]) == 3
