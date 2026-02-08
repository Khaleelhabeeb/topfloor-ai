"""
Tools Module - Collection of tools for AI agents

This module provides various tools for different agent types:
- Finance tools for financial analysis
- Data analysis tools for data processing and visualization
- Research tools for web research
- Chart templates for consistent visualizations

Note: Tools are imported lazily to avoid dependency issues.
Use direct imports when needed, e.g.:
    from app.tools.chart_templates import list_chart_templates
"""

# Lazy imports to avoid loading all dependencies at once
def __getattr__(name):
    """Lazy import of tool functions"""
    
    # Finance tools
    if name in ["fetch_market_data", "analyze_bank_statement", "create_budget", 
                "calculate_financial_metrics", "forecast_expenses"]:
        from app.tools import finance_tools
        return getattr(finance_tools, name)
    
    # Data analysis tools
    elif name in ["load_dataset", "clean_data", "analyze_data", 
                  "create_visualization", "generate_chart", "build_dashboard"]:
        from app.tools import data_analysis_tools
        return getattr(data_analysis_tools, name)
    
    # Research tools
    elif name in ["web_search", "fetch_content", "verify_source", "compile_research"]:
        from app.tools import research_tools
        return getattr(research_tools, name)
    
    # Chart templates
    elif name in ["ChartTemplate", "get_chart_template", "list_chart_templates",
                  "create_chart_from_template", "get_template_info"]:
        from app.tools import chart_templates
        return getattr(chart_templates, name)
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Finance tools
    "fetch_market_data",
    "analyze_bank_statement",
    "create_budget",
    "calculate_financial_metrics",
    "forecast_expenses",
    
    # Data analysis tools
    "load_dataset",
    "clean_data",
    "analyze_data",
    "create_visualization",
    "generate_chart",
    "build_dashboard",
    
    # Research tools
    "web_search",
    "fetch_content",
    "verify_source",
    "compile_research",
    
    # Chart templates
    "ChartTemplate",
    "get_chart_template",
    "list_chart_templates",
    "create_chart_from_template",
    "get_template_info",
]
