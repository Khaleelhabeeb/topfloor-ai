"""
Tests for document templates
"""

import pytest
from app.tools.document_templates import (
    get_template,
    list_templates,
    FinanceReportTemplate,
    DataAnalysisReportTemplate,
    ResearchReportTemplate,
    TeamLeadStatusReportTemplate
)


def test_list_templates():
    """Test listing all available templates"""
    templates = list_templates()
    
    assert isinstance(templates, dict)
    assert "finance" in templates
    assert "data_analyst" in templates
    assert "researcher" in templates
    assert "team_lead" in templates
    
    assert "financial_report" in templates["finance"]
    assert "data_analysis_report" in templates["data_analyst"]
    assert "research_report" in templates["researcher"]
    assert "status_report" in templates["team_lead"]


def test_list_templates_filtered():
    """Test listing templates for specific agent"""
    templates = list_templates("finance")
    
    assert isinstance(templates, dict)
    assert "finance" in templates
    assert len(templates) == 1


def test_get_template_finance():
    """Test getting finance template"""
    template = get_template("finance", "financial_report")
    
    assert template is not None
    assert isinstance(template, FinanceReportTemplate)
    assert template.agent_type == "finance"
    assert template.template_name == "financial_report"


def test_get_template_data_analyst():
    """Test getting data analyst template"""
    template = get_template("data_analyst", "data_analysis_report")
    
    assert template is not None
    assert isinstance(template, DataAnalysisReportTemplate)
    assert template.agent_type == "data_analyst"


def test_get_template_researcher():
    """Test getting researcher template"""
    template = get_template("researcher", "research_report")
    
    assert template is not None
    assert isinstance(template, ResearchReportTemplate)
    assert template.agent_type == "researcher"


def test_get_template_team_lead():
    """Test getting team lead template"""
    template = get_template("team_lead", "status_report")
    
    assert template is not None
    assert isinstance(template, TeamLeadStatusReportTemplate)
    assert template.agent_type == "team_lead"


def test_get_template_default():
    """Test getting default template for agent"""
    template = get_template("finance")
    
    assert template is not None
    assert isinstance(template, FinanceReportTemplate)


def test_get_template_invalid():
    """Test getting invalid template"""
    template = get_template("invalid_agent")
    
    assert template is None


def test_finance_template_build_content():
    """Test building content with finance template"""
    template = FinanceReportTemplate()
    
    data = {
        "title": "Q4 Financial Report",
        "period": "Q4 2025",
        "summary": "Strong financial performance this quarter.",
        "market_data": {
            "AAPL": {"price": 150.0, "change": 2.5, "change_percent": 1.7, "volume": 1000000}
        },
        "financial_metrics": {
            "revenue": "$1.2M",
            "profit_margin": "15%",
            "roi": "12%"
        },
        "analysis": "The company showed strong growth...",
        "recommendations": ["Increase savings", "Diversify portfolio"]
    }
    
    content = template.build_content(data)
    
    assert content["title"] == "Q4 Financial Report"
    assert content["subtitle"] == "Q4 2025"
    assert content["author"] == "Finance Agent - TopFloor AI"
    assert content["summary"] == "Strong financial performance this quarter."
    assert len(content["sections"]) > 0
    
    # Check sections
    section_titles = [s["title"] for s in content["sections"]]
    assert "Market Overview" in section_titles
    assert "Key Financial Metrics" in section_titles
    assert "Financial Analysis" in section_titles
    assert "Recommendations" in section_titles


def test_data_analyst_template_build_content():
    """Test building content with data analyst template"""
    template = DataAnalysisReportTemplate()
    
    data = {
        "title": "Sales Data Analysis",
        "dataset_name": "Q4 Sales Data",
        "summary": "Analysis of Q4 sales performance.",
        "dataset_info": "Dataset contains 10,000 records...",
        "statistics": "Mean: 100, Median: 95, Std: 15",
        "insights": ["Sales increased by 20%", "Top product is Product A"],
        "recommendations": ["Focus on Product A", "Expand to new markets"]
    }
    
    content = template.build_content(data)
    
    assert content["title"] == "Sales Data Analysis"
    assert content["subtitle"] == "Q4 Sales Data"
    assert content["author"] == "Data Analyst - TopFloor AI"
    assert len(content["sections"]) > 0
    
    # Check sections
    section_titles = [s["title"] for s in content["sections"]]
    assert "Dataset Information" in section_titles
    assert "Statistical Summary" in section_titles
    assert "Key Insights" in section_titles
    assert "Recommendations" in section_titles


def test_researcher_template_build_content():
    """Test building content with researcher template"""
    template = ResearchReportTemplate()
    
    data = {
        "title": "AI Market Research",
        "topic": "Current state of AI market",
        "summary": "Comprehensive analysis of AI market trends.",
        "findings": ["AI market growing at 30% CAGR", "Major players include..."],
        "analysis": "The AI market is experiencing rapid growth...",
        "conclusions": "AI adoption will continue to accelerate.",
        "sources": ["Source 1", "Source 2", "Source 3"]
    }
    
    content = template.build_content(data)
    
    assert content["title"] == "AI Market Research"
    assert content["subtitle"] == "Current state of AI market"
    assert content["author"] == "Researcher - TopFloor AI"
    assert len(content["sections"]) > 0
    
    # Check sections
    section_titles = [s["title"] for s in content["sections"]]
    assert "Research Topic" in section_titles
    assert "Key Findings" in section_titles
    assert "Detailed Analysis" in section_titles
    assert "Conclusions" in section_titles
    assert "References" in section_titles


def test_team_lead_template_build_content():
    """Test building content with team lead template"""
    template = TeamLeadStatusReportTemplate()
    
    data = {
        "title": "Weekly Team Status",
        "period": "Week of Jan 1-7, 2026",
        "summary": "Team is on track with all deliverables.",
        "team_status": "All agents are operational.",
        "agent_statuses": {
            "finance": {"status": "available", "current_task": "None", "tasks_in_queue": 0},
            "data_analyst": {"status": "busy", "current_task": "Data analysis", "tasks_in_queue": 2}
        },
        "completed_tasks": ["Task 1", "Task 2"],
        "in_progress_tasks": ["Task 3"],
        "pending_tasks": ["Task 4", "Task 5"],
        "blockers": ["Waiting for API access"],
        "metrics": {
            "tasks_completed": 10,
            "average_completion_time": "2 hours"
        }
    }
    
    content = template.build_content(data)
    
    assert content["title"] == "Weekly Team Status"
    assert content["subtitle"] == "Week of Jan 1-7, 2026"
    assert content["author"] == "Team Lead - TopFloor AI"
    assert len(content["sections"]) > 0
    
    # Check sections
    section_titles = [s["title"] for s in content["sections"]]
    assert "Team Overview" in section_titles
    assert "Agent Status" in section_titles
    assert "Task Summary" in section_titles
    assert "Blockers and Issues" in section_titles
    assert "Performance Metrics" in section_titles
