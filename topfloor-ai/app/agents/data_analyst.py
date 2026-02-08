"""
Data Analyst Agent - Data analysis and visualization specialist
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from google.adk.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition
from app.tools.data_analysis_tools import build_dashboard as build_dashboard_tool
from app.tools.document_templates import get_template


class DataAnalystAgent(BaseAgent):
    """
    Data analysis specialist that processes datasets,
    performs statistical analysis, and creates visualizations.
    """
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build data analysis tools.
        
        Returns:
            List of data analysis tools including CodeExecution
        """
        tools = []
        
        # Code execution is enabled via code_executor parameter in base agent
        # Not added as a tool here
        
        # Load data tool
        @FunctionTool
        def load_data(
            source: str,
            source_path: str,
            file_format: str = "auto"
        ) -> Dict[str, Any]:
            """
            Load data from various sources into analysis environment.
            
            Args:
                source: Data source type (upload, url)
                source_path: Path or URL to the data
                file_format: File format (csv, json, parquet, auto)
                
            Returns:
                Data loading confirmation with summary
            """
            return {
                "status": "loaded",
                "source": source,
                "source_path": source_path,
                "format": file_format,
                "rows": 0,
                "columns": 0,
                "preview": []
            }
        
        # Create visualization tool
        @FunctionTool
        def create_visualization(
            chart_type: str,
            data_config: Dict[str, Any],
            title: str,
            description: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Create data visualizations and charts.
            
            Args:
                chart_type: Type of chart (line, bar, scatter, pie, heatmap)
                data_config: Configuration for the chart (x, y, labels, etc.)
                title: Chart title
                description: Optional chart description
                
            Returns:
                Visualization creation confirmation
            """
            viz_id = f"viz_{chart_type}_{datetime.now().timestamp()}"
            
            return {
                "status": "created",
                "visualization_id": viz_id,
                "chart_type": chart_type,
                "title": title,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
        
        # Build dashboard tool
        @FunctionTool
        def build_dashboard(
            components_json: str,
            layout_json: Optional[str] = None,
            title: str = "Interactive Dashboard",
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Build a dashboard payload for frontend rendering.
            
            Args:
                components_json: JSON string of component list. Each component should contain:
                    - type: Component type ('chart', 'table', 'metric', 'text')
                    - data: Data for the component (DataFrame or dict)
                    - config: Component-specific configuration
                    Example: '[{"type": "chart", "data": {...}, "config": {...}}]'
                layout_json: Optional JSON string of layout configuration (columns, theme)
                    Example: '{"columns": 2, "theme": "light"}'
                title: Dashboard title
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dashboard render payload
            """
            # Parse JSON strings
            try:
                components = json.loads(components_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"Invalid JSON format for components: {str(e)}"
                }
            
            layout = None
            if layout_json:
                try:
                    layout = json.loads(layout_json)
                except json.JSONDecodeError as e:
                    return {
                        "status": "error",
                        "message": f"Invalid JSON format for layout: {str(e)}"
                    }
            
            return build_dashboard_tool(
                components=components,
                layout=layout,
                title=title,
                output_dir=output_dir
            )
        
        # Generate insights tool
        @FunctionTool
        def generate_insights(
            analysis_results_json: str,
            num_insights: int = 5
        ) -> List[str]:
            """
            Generate actionable insights from analysis results.
            
            Args:
                analysis_results_json: JSON string of analysis results
                    Example: '{"mean": 50, "median": 45, "trend": "increasing"}'
                num_insights: Number of insights to generate
                
            Returns:
                List of insights
            """
            # Parse JSON string
            try:
                analysis_results = json.loads(analysis_results_json)
            except json.JSONDecodeError as e:
                return [f"Error parsing analysis results: {str(e)}"]
            
            # Simple insight generation - in production, use LLM
            return [
                "Insight placeholder 1",
                "Insight placeholder 2",
                "Insight placeholder 3"
            ][:num_insights]
        
        # Generate Data Analysis Report Tool
        @FunctionTool
        def generate_analysis_report(
            data_json: str,
            format: str = "pdf",
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Generate a professional data analysis report payload.
            
            This tool creates comprehensive data analysis reports with visualizations,
            statistical summaries, and insights. Perfect for presenting analysis results.
            
            Args:
                data_json: JSON string of data analysis report data including:
                    - title: Report title (required)
                    - dataset_name: Name of the dataset
                    - dataset_info: Dataset description and metadata
                    - summary: Executive summary
                    - statistics: Statistical summary text
                    - data_quality: Data quality assessment
                    - insights: List of key insights
                    - visualizations: List of visualization file paths
                    - recommendations: List of recommendations
                    - statistics_tables: Optional list of statistical tables
                    - statistics_charts: Optional list of chart paths
                    Example: '{"title": "Sales Analysis", "dataset_name": "Q4 Sales", "insights": [...]}'
                format: Output format hint for frontend ("pdf" or "docx")
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with structured content payload for frontend rendering
                
            Example:
                >>> data_json = '{"title": "Sales Data Analysis", "dataset_name": "Q4 Sales Data", "insights": ["Sales increased by 20%"]}'
                >>> result = generate_analysis_report(data_json, "pdf")
            """
            # Parse JSON string
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": f"Invalid JSON format for data: {str(e)}"
                }
            
            template = get_template("data_analyst", "data_analysis_report")
            if not template:
                return {
                    "status": "error",
                    "message": "No data analysis report template available"
                }
            content = template.build_content(data)
            return {
                "status": "success",
                "render_type": "report",
                "format": format,
                "template": "data_analysis_report",
                "content": content,
                "render_hint": "frontend"
            }
        
        # Chart Generation Tool
        @FunctionTool
        def generate_chart(
            data_json: str,
            chart_type: str,
            config_json: Optional[str] = None,
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Generate data visualization chart payloads.
            
            Creates professional charts for data visualization. Supports multiple chart types
            and both static (PNG) and interactive (HTML) formats.
            
            Args:
                data_json: JSON string of chart data including:
                    - x: List of x-axis values (for line, bar, scatter)
                    - y: List of y-axis values or list of lists for multiple series
                    - labels: List of labels (for pie charts)
                    - values: List of values (for pie charts)
                    - matrix: 2D array for heatmaps
                    - series_names: Optional list of series names for legend
                    Example: '{"x": [1,2,3], "y": [10,20,30]}'
                chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', 'histogram', 'heatmap')
                config_json: Optional JSON string of configuration:
                    - title: Chart title
                    - xlabel: X-axis label
                    - ylabel: Y-axis label
                    - colors: List of colors
                    - width: Chart width
                    - height: Chart height
                    - interactive: Boolean for interactive HTML output
                    Example: '{"title": "Sales Trend", "xlabel": "Month"}'
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
        
        # Generate Report with Charts Tool
        @FunctionTool
        def create_report_with_charts(
            title: str,
            sections: List[Dict[str, Any]],
            format: str = "pdf",
            output_dir: str = "/tmp"
        ) -> Dict[str, Any]:
            """
            Create a data analysis report payload with embedded chart specs.
            
            This convenience tool generates charts from data and embeds them in a report
            automatically. Perfect for creating complete analysis reports quickly.
            
            Args:
                title: Report title
                sections: List of section dictionaries, each containing:
                    - title: Section title
                    - content: Section text content
                    - chart_data: Optional dict with chart data to generate:
                        - data: Chart data (x, y, labels, values, etc.)
                        - chart_type: Type of chart
                        - config: Chart configuration
                    - charts: Optional list of pre-generated chart paths
                    - tables: Optional list of table data
                format: Output format hint for frontend ("pdf" or "docx")
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with structured content payload for frontend rendering
                
            Example:
                >>> sections = [
                ...     {
                ...         "title": "Sales Trend",
                ...         "content": "Monthly sales show upward trend...",
                ...         "chart_data": {
                ...             "data": {"x": ["Jan", "Feb", "Mar"], "y": [100, 120, 140]},
                ...             "chart_type": "line",
                ...             "config": {"title": "Monthly Sales"}
                ...         }
                ...     }
                ... ]
                >>> result = create_report_with_charts("Sales Analysis", sections, "pdf")
            """
            normalized_sections = []
            for section in sections:
                chart_data = section.get("chart_data")
                chart_spec = None
                if chart_data:
                    chart_spec = {
                        "chart_type": chart_data.get("chart_type"),
                        "data": chart_data.get("data"),
                        "config": chart_data.get("config") or {}
                    }
                normalized_sections.append({
                    "title": section.get("title"),
                    "content": section.get("content"),
                    "chart_spec": chart_spec,
                    "charts": section.get("charts") or [],
                    "tables": section.get("tables") or []
                })
            return {
                "status": "success",
                "render_type": "report",
                "format": format,
                "template": "data_analysis_report",
                "content": {
                    "title": title,
                    "sections": normalized_sections
                },
                "render_hint": "frontend"
            }
        
        tools.extend([
            load_data,
            create_visualization,
            build_dashboard,
            generate_insights,
            generate_analysis_report,
            generate_chart,
            create_report_with_charts
        ])
        
        return tools
