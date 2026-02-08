"""
Chart Templates - Predefined chart configurations for different use cases

This module provides chart templates for common visualization scenarios
used by Finance Agent and Data Analyst Agent. Templates ensure consistent
styling and appropriate chart types for different data types.
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class ChartTemplate(Enum):
    """Predefined chart templates"""
    # Finance Agent Templates
    STOCK_PRICE_TREND = "stock_price_trend"
    PORTFOLIO_ALLOCATION = "portfolio_allocation"
    EXPENSE_BREAKDOWN = "expense_breakdown"
    INCOME_VS_EXPENSES = "income_vs_expenses"
    BUDGET_COMPARISON = "budget_comparison"
    FINANCIAL_METRICS = "financial_metrics"
    MARKET_COMPARISON = "market_comparison"
    
    # Data Analyst Templates
    TIME_SERIES = "time_series"
    DISTRIBUTION = "distribution"
    CORRELATION_HEATMAP = "correlation_heatmap"
    CATEGORY_COMPARISON = "category_comparison"
    SCATTER_RELATIONSHIP = "scatter_relationship"
    STACKED_BAR = "stacked_bar"
    MULTI_LINE = "multi_line"
    BOX_PLOT = "box_plot"


class ChartTemplateConfig:
    """Base class for chart template configurations"""
    
    def __init__(
        self,
        name: str,
        chart_type: str,
        description: str,
        default_config: Dict[str, Any],
        data_requirements: Dict[str, str]
    ):
        self.name = name
        self.chart_type = chart_type
        self.description = description
        self.default_config = default_config
        self.data_requirements = data_requirements
    
    def get_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get chart configuration with optional custom overrides
        
        Args:
            custom_config: Optional dictionary to override default config
            
        Returns:
            Merged configuration dictionary
        """
        config = self.default_config.copy()
        if custom_config:
            config.update(custom_config)
        return config
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that data contains required fields
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for field, description in self.data_requirements.items():
            if field not in data:
                return False, f"Missing required field '{field}': {description}"
        return True, None


# Finance Agent Chart Templates

STOCK_PRICE_TREND_TEMPLATE = ChartTemplateConfig(
    name="Stock Price Trend",
    chart_type="line",
    description="Line chart showing stock price movement over time",
    default_config={
        "title": "Stock Price Trend",
        "xlabel": "Date",
        "ylabel": "Price ($)",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Date values (list of dates or timestamps)",
        "y": "Price values (list of numbers)"
    }
)

PORTFOLIO_ALLOCATION_TEMPLATE = ChartTemplateConfig(
    name="Portfolio Allocation",
    chart_type="pie",
    description="Pie chart showing portfolio asset allocation",
    default_config={
        "title": "Portfolio Allocation",
        "figsize": (10, 10),
        "dpi": 300,
        "interactive": False
    },
    data_requirements={
        "labels": "Asset names (list of strings)",
        "values": "Asset values or percentages (list of numbers)"
    }
)

EXPENSE_BREAKDOWN_TEMPLATE = ChartTemplateConfig(
    name="Expense Breakdown",
    chart_type="bar",
    description="Bar chart showing expenses by category",
    default_config={
        "title": "Expense Breakdown by Category",
        "xlabel": "Category",
        "ylabel": "Amount ($)",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "color": "#e74c3c",
        "interactive": False
    },
    data_requirements={
        "x": "Category names (list of strings)",
        "y": "Expense amounts (list of numbers)"
    }
)

INCOME_VS_EXPENSES_TEMPLATE = ChartTemplateConfig(
    name="Income vs Expenses",
    chart_type="line",
    description="Multi-line chart comparing income and expenses over time",
    default_config={
        "title": "Income vs Expenses",
        "xlabel": "Month",
        "ylabel": "Amount ($)",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Time periods (list of dates or month names)",
        "y": "List of two series: [income_values, expense_values]",
        "series_names": "Optional: ['Income', 'Expenses']"
    }
)

BUDGET_COMPARISON_TEMPLATE = ChartTemplateConfig(
    name="Budget Comparison",
    chart_type="bar",
    description="Bar chart comparing budgeted vs actual spending",
    default_config={
        "title": "Budget vs Actual Spending",
        "xlabel": "Category",
        "ylabel": "Amount ($)",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Category names (list of strings)",
        "y": "List of two series: [budgeted_values, actual_values]",
        "series_names": "Optional: ['Budgeted', 'Actual']"
    }
)

FINANCIAL_METRICS_TEMPLATE = ChartTemplateConfig(
    name="Financial Metrics",
    chart_type="bar",
    description="Bar chart displaying key financial metrics",
    default_config={
        "title": "Key Financial Metrics",
        "xlabel": "Metric",
        "ylabel": "Value",
        "figsize": (10, 6),
        "dpi": 300,
        "grid": True,
        "color": "#3498db",
        "interactive": False
    },
    data_requirements={
        "x": "Metric names (list of strings)",
        "y": "Metric values (list of numbers)"
    }
)

MARKET_COMPARISON_TEMPLATE = ChartTemplateConfig(
    name="Market Comparison",
    chart_type="line",
    description="Multi-line chart comparing multiple market instruments",
    default_config={
        "title": "Market Comparison",
        "xlabel": "Date",
        "ylabel": "Normalized Price",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Date values (list of dates)",
        "y": "List of price series for each instrument",
        "series_names": "Instrument names (list of strings)"
    }
)


# Data Analyst Chart Templates

TIME_SERIES_TEMPLATE = ChartTemplateConfig(
    name="Time Series",
    chart_type="line",
    description="Line chart for time series data analysis",
    default_config={
        "title": "Time Series Analysis",
        "xlabel": "Time",
        "ylabel": "Value",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Time values (list of dates or timestamps)",
        "y": "Measured values (list of numbers)"
    }
)

DISTRIBUTION_TEMPLATE = ChartTemplateConfig(
    name="Distribution",
    chart_type="histogram",
    description="Histogram showing data distribution",
    default_config={
        "title": "Data Distribution",
        "xlabel": "Value",
        "ylabel": "Frequency",
        "figsize": (10, 6),
        "dpi": 300,
        "bins": 30,
        "color": "#9b59b6",
        "interactive": False
    },
    data_requirements={
        "values": "Data values (list of numbers)"
    }
)

CORRELATION_HEATMAP_TEMPLATE = ChartTemplateConfig(
    name="Correlation Heatmap",
    chart_type="heatmap",
    description="Heatmap showing correlations between variables",
    default_config={
        "title": "Correlation Matrix",
        "figsize": (10, 8),
        "dpi": 300,
        "colormap": "RdBu",
        "interactive": False
    },
    data_requirements={
        "matrix": "Correlation matrix (2D array)",
        "xlabels": "Variable names for x-axis (list of strings)",
        "ylabels": "Variable names for y-axis (list of strings)"
    }
)

CATEGORY_COMPARISON_TEMPLATE = ChartTemplateConfig(
    name="Category Comparison",
    chart_type="bar",
    description="Bar chart comparing values across categories",
    default_config={
        "title": "Category Comparison",
        "xlabel": "Category",
        "ylabel": "Value",
        "figsize": (10, 6),
        "dpi": 300,
        "grid": True,
        "color": "#2ecc71",
        "interactive": False
    },
    data_requirements={
        "x": "Category names (list of strings)",
        "y": "Values (list of numbers)"
    }
)

SCATTER_RELATIONSHIP_TEMPLATE = ChartTemplateConfig(
    name="Scatter Relationship",
    chart_type="scatter",
    description="Scatter plot showing relationship between two variables",
    default_config={
        "title": "Variable Relationship",
        "xlabel": "Variable X",
        "ylabel": "Variable Y",
        "figsize": (10, 8),
        "dpi": 300,
        "grid": True,
        "color": "#e67e22",
        "interactive": False
    },
    data_requirements={
        "x": "X-axis values (list of numbers)",
        "y": "Y-axis values (list of numbers)"
    }
)

STACKED_BAR_TEMPLATE = ChartTemplateConfig(
    name="Stacked Bar",
    chart_type="bar",
    description="Stacked bar chart for multi-category comparison",
    default_config={
        "title": "Stacked Bar Comparison",
        "xlabel": "Category",
        "ylabel": "Value",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "Category names (list of strings)",
        "y": "List of value series for stacking",
        "series_names": "Series names for legend (list of strings)"
    }
)

MULTI_LINE_TEMPLATE = ChartTemplateConfig(
    name="Multi-Line",
    chart_type="line",
    description="Multi-line chart for comparing multiple series",
    default_config={
        "title": "Multi-Series Comparison",
        "xlabel": "X-axis",
        "ylabel": "Y-axis",
        "figsize": (12, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "x": "X-axis values (list)",
        "y": "List of Y-axis series",
        "series_names": "Series names for legend (list of strings)"
    }
)

BOX_PLOT_TEMPLATE = ChartTemplateConfig(
    name="Box Plot",
    chart_type="box",
    description="Box plot showing data distribution and outliers",
    default_config={
        "title": "Box Plot Analysis",
        "xlabel": "Category",
        "ylabel": "Value",
        "figsize": (10, 6),
        "dpi": 300,
        "grid": True,
        "interactive": False
    },
    data_requirements={
        "values": "Data values (list of numbers) or grouped data"
    }
)


# Template Registry
CHART_TEMPLATES: Dict[str, ChartTemplateConfig] = {
    # Finance templates
    ChartTemplate.STOCK_PRICE_TREND.value: STOCK_PRICE_TREND_TEMPLATE,
    ChartTemplate.PORTFOLIO_ALLOCATION.value: PORTFOLIO_ALLOCATION_TEMPLATE,
    ChartTemplate.EXPENSE_BREAKDOWN.value: EXPENSE_BREAKDOWN_TEMPLATE,
    ChartTemplate.INCOME_VS_EXPENSES.value: INCOME_VS_EXPENSES_TEMPLATE,
    ChartTemplate.BUDGET_COMPARISON.value: BUDGET_COMPARISON_TEMPLATE,
    ChartTemplate.FINANCIAL_METRICS.value: FINANCIAL_METRICS_TEMPLATE,
    ChartTemplate.MARKET_COMPARISON.value: MARKET_COMPARISON_TEMPLATE,
    
    # Data analyst templates
    ChartTemplate.TIME_SERIES.value: TIME_SERIES_TEMPLATE,
    ChartTemplate.DISTRIBUTION.value: DISTRIBUTION_TEMPLATE,
    ChartTemplate.CORRELATION_HEATMAP.value: CORRELATION_HEATMAP_TEMPLATE,
    ChartTemplate.CATEGORY_COMPARISON.value: CATEGORY_COMPARISON_TEMPLATE,
    ChartTemplate.SCATTER_RELATIONSHIP.value: SCATTER_RELATIONSHIP_TEMPLATE,
    ChartTemplate.STACKED_BAR.value: STACKED_BAR_TEMPLATE,
    ChartTemplate.MULTI_LINE.value: MULTI_LINE_TEMPLATE,
    ChartTemplate.BOX_PLOT.value: BOX_PLOT_TEMPLATE,
}


def get_chart_template(template_name: str) -> Optional[ChartTemplateConfig]:
    """
    Get a chart template by name
    
    Args:
        template_name: Name of the template (use ChartTemplate enum values)
        
    Returns:
        ChartTemplateConfig object or None if not found
        
    Example:
        >>> template = get_chart_template("stock_price_trend")
        >>> config = template.get_config({"title": "AAPL Stock Price"})
    """
    return CHART_TEMPLATES.get(template_name)


def list_chart_templates(agent_type: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List available chart templates, optionally filtered by agent type
    
    Args:
        agent_type: Optional agent type to filter by ('finance' or 'data_analyst')
        
    Returns:
        List of template information dictionaries
        
    Example:
        >>> templates = list_chart_templates("finance")
        >>> for t in templates:
        ...     print(f"{t['name']}: {t['description']}")
    """
    templates = []
    
    for template_key, template_config in CHART_TEMPLATES.items():
        # Filter by agent type if specified
        if agent_type:
            if agent_type == "finance" and not template_key.startswith(("stock", "portfolio", "expense", "income", "budget", "financial", "market")):
                continue
            if agent_type == "data_analyst" and not template_key.startswith(("time", "distribution", "correlation", "category", "scatter", "stacked", "multi", "box")):
                continue
        
        templates.append({
            "key": template_key,
            "name": template_config.name,
            "chart_type": template_config.chart_type,
            "description": template_config.description,
            "data_requirements": template_config.data_requirements
        })
    
    return templates


def create_chart_from_template(
    template_name: str,
    data: Dict[str, Any],
    custom_config: Optional[Dict[str, Any]] = None,
    output_dir: str = "/tmp"
) -> Dict[str, Any]:
    """
    Create a chart using a predefined template
    
    This is a convenience function that combines template lookup, data validation,
    and chart generation in one call.
    
    Args:
        template_name: Name of the template to use
        data: Data dictionary matching template requirements
        custom_config: Optional configuration overrides
        output_dir: Directory to save the chart
        
    Returns:
        Dictionary with chart render payload
        
    Example:
        >>> data = {
        ...     "x": ["Jan", "Feb", "Mar", "Apr"],
        ...     "y": [1000, 1500, 1200, 1800]
        ... }
        >>> result = create_chart_from_template(
        ...     "expense_breakdown",
        ...     data,
        ...     custom_config={"title": "Q1 Expenses"}
        ... )
        >>> print(result["render_type"])
        chart
    """
    # Get template
    template = get_chart_template(template_name)
    
    if not template:
        return {
            "status": "error",
            "message": f"Template not found: {template_name}. Use list_chart_templates() to see available templates."
        }
    
    # Validate data
    is_valid, error_message = template.validate_data(data)
    if not is_valid:
        return {
            "status": "error",
            "message": f"Data validation failed: {error_message}",
            "template": template_name,
            "data_requirements": template.data_requirements
        }
    
    # Get configuration
    config = template.get_config(custom_config)
    
    return {
        "status": "success",
        "render_type": "chart",
        "template": template_name,
        "chart_type": template.chart_type,
        "data": data,
        "config": config,
        "render_hint": "frontend"
    }


def get_template_info(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific template
    
    Args:
        template_name: Name of the template
        
    Returns:
        Dictionary with template information or None if not found
        
    Example:
        >>> info = get_template_info("stock_price_trend")
        >>> print(info["description"])
        Line chart showing stock price movement over time
    """
    template = get_chart_template(template_name)
    
    if not template:
        return None
    
    return {
        "name": template.name,
        "chart_type": template.chart_type,
        "description": template.description,
        "default_config": template.default_config,
        "data_requirements": template.data_requirements
    }


# Export public API
__all__ = [
    "ChartTemplate",
    "ChartTemplateConfig",
    "get_chart_template",
    "list_chart_templates",
    "create_chart_from_template",
    "get_template_info",
    "CHART_TEMPLATES"
]
