"""
Mock Response System for Free Tier API Rate Limits

This module provides mock responses when API rate limits are exceeded.
To disable mocking and use real API responses, set USE_MOCK_RESPONSES=false in .env

Usage:
    1. Set USE_MOCK_RESPONSES=true in .env to enable mocking
    2. When you get a paid API key, set USE_MOCK_RESPONSES=false
    3. That's it! No code changes needed.
"""

import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Check if mock responses are enabled
USE_MOCK_RESPONSES = os.getenv("USE_MOCK_RESPONSES", "false").lower() == "true"


def get_mock_agent_response(agent_type: str, message: str) -> Dict[str, Any]:
    """
    Generate a mock response for an agent based on its type.
    
    Args:
        agent_type: Type of agent (finance, researcher, data_analyst, team_lead)
        message: User's message
        
    Returns:
        Mock response dictionary
    """
    mock_responses = {
        "finance": {
            "response": f"""Hello! I'm the Finance Agent. I received your message: "{message}"

Here's what I can help you with:

**Market Analysis:**
- Real-time stock prices and crypto data
- Historical performance tracking
- Investment trend analysis

**Personal Finance:**
- Budget planning and creation
- Expense tracking and categorization
- Bank statement analysis

**Financial Metrics:**
- ROI calculations
- Savings rate analysis
- Debt-to-income ratios

**Professional Reports:**
- PDF financial reports with charts
- Comprehensive analysis documents

*Note: This is a mock response due to API rate limits. With a paid API key, I'll provide real-time data and analysis.*

How can I assist you with your finances today?""",
            "metadata": {
                "agent_type": "finance",
                "mock_response": True,
                "reason": "API rate limit - using mock response"
            }
        },
        "researcher": {
            "response": f"""Hello! I'm the Researcher Agent. I received your message: "{message}"

Here's what I can help you with:

**Web Research:**
- Multi-source information gathering
- Comprehensive topic research
- Fact verification and source checking

**Source Analysis:**
- Credibility assessment
- Citation management
- Contradiction detection

**Research Compilation:**
- Structured research documents
- Executive summaries
- Annotated bibliographies

**Professional Reports:**
- PDF research reports
- Source analysis tables
- Visual data presentations

*Note: This is a mock response due to API rate limits. With a paid API key, I'll perform real web searches and provide actual research.*

What topic would you like me to research?""",
            "metadata": {
                "agent_type": "researcher",
                "mock_response": True,
                "reason": "API rate limit - using mock response"
            }
        },
        "data_analyst": {
            "response": f"""Hello! I'm the Data Analyst Agent. I received your message: "{message}"

Here's what I can help you with:

**Data Processing:**
- Load data from CSV, JSON, Excel, URLs
- Data cleaning and validation
- Statistical analysis

**Visualizations:**
- Line charts, bar charts, scatter plots
- Pie charts, histograms, heatmaps
- Interactive dashboards

**Analysis:**
- Descriptive statistics
- Correlation analysis
- Trend identification
- Pattern recognition

**Professional Reports:**
- PDF/DOCX analysis reports
- Embedded charts and tables
- Executive summaries with insights

*Note: This is a mock response due to API rate limits. With a paid API key, I'll analyze real data and create actual visualizations.*

What data would you like me to analyze?""",
            "metadata": {
                "agent_type": "data_analyst",
                "mock_response": True,
                "reason": "API rate limit - using mock response"
            }
        },
        "team_lead": {
            "response": f"""Hello! I'm the Team Lead Agent. I received your message: "{message}"

Here's what I can help you with:

**Project Coordination:**
- Break down complex projects into tasks
- Assign tasks to specialized agents
- Monitor progress across the team

**Status Reporting:**
- Comprehensive status reports
- Progress tracking with metrics
- Team performance summaries

**Workload Management:**
- Balance tasks across agents
- Check agent availability
- Prioritize critical work

**Task Management:**
- Create and assign tasks
- Update task status
- Track completed and failed tasks

*Note: This is a mock response due to API rate limits. With a paid API key, I'll coordinate real tasks and provide actual status updates.*

What project can I help you coordinate?""",
            "metadata": {
                "agent_type": "team_lead",
                "mock_response": True,
                "reason": "API rate limit - using mock response"
            }
        }
    }
    
    return mock_responses.get(agent_type, {
        "response": f"Mock response for {agent_type} agent. Message received: {message}",
        "metadata": {
            "agent_type": agent_type,
            "mock_response": True,
            "reason": "API rate limit - using mock response"
        }
    })


def should_use_mock_response(error_message: str) -> bool:
    """
    Determine if we should use a mock response based on the error.
    
    Args:
        error_message: Error message from the API
        
    Returns:
        True if we should use mock response, False otherwise
    """
    if not USE_MOCK_RESPONSES:
        return False
    
    # Check for rate limit errors
    rate_limit_indicators = [
        "rate limit",
        "quota exceeded",
        "too many requests",
        "429",
        "RESOURCE_EXHAUSTED"
    ]
    
    error_lower = error_message.lower()
    return any(indicator in error_lower for indicator in rate_limit_indicators)


def log_mock_usage(agent_type: str, reason: str):
    """Log when mock responses are used"""
    logger.info(
        f"Using mock response for {agent_type} agent. "
        f"Reason: {reason}. "
        f"To disable mocking, set USE_MOCK_RESPONSES=false in .env"
    )
