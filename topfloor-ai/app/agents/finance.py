"""
Finance Agent - Financial advisor and analyst specialist
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from google.adk.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.registry import AgentDefinition
from app.tools import finance_tools
from app.tools.document_templates import get_template


class FinanceAgent(BaseAgent):
    """
    Financial advisor and analyst that provides market analysis,
    budgeting, expense tracking, and financial forecasting.
    """
    
    def build_tools(self) -> List[FunctionTool]:
        """
        Build finance tools.
        
        Returns:
            List of finance tools for market data, budgeting, and analysis
        """
        tools = []
        
        # Market Data Tool
        @FunctionTool
        def fetch_market_data(
            symbol: str,
            timeframe: str = "1d",
            data_source: str = "yahoo"
        ) -> dict:
            """
            Fetch real-time and historical market data for stocks, crypto, commodities, or forex.
            
            Args:
                symbol: Stock ticker symbol (e.g., 'AAPL', 'BTC-USD', 'EURUSD')
                timeframe: Time period for data ('1d', '1w', '1m', '3m', '1y', '5y')
                data_source: Data provider ('yahoo' or 'alpha_vantage')
                
            Returns:
                Market data including current price, change, volume, and historical data
            """
            return finance_tools.fetch_market_data(symbol, timeframe, data_source)
        
        # Bank Statement Analysis Tool
        @FunctionTool
        def analyze_bank_statement(
            file_path: str,
            file_type: str = "csv"
        ) -> dict:
            """
            Parse and analyze bank statement to categorize transactions and calculate metrics.
            
            Args:
                file_path: Path to the bank statement file
                file_type: File format ('csv', 'excel', 'pdf')
                
            Returns:
                Analysis including income, expenses, savings rate, and categorized spending
            """
            return finance_tools.analyze_bank_statement(file_path, file_type)
        
        # Budget Creation Tool
        @FunctionTool
        def create_budget(
            income: float,
            expenses_json: str,
            goals_json: str = None
        ) -> dict:
            """
            Create a budget plan based on income, expenses, and financial goals.
            
            Args:
                income: Monthly income amount
                expenses_json: JSON string of expense categories and amounts (e.g., '{"housing": 1200, "food": 600}')
                goals_json: Optional JSON string of savings goals and target amounts (e.g., '{"emergency": 500}')
                
            Returns:
                Budget plan with percentages, available funds, and recommendations
            """
            import json
            expenses = json.loads(expenses_json)
            goals = json.loads(goals_json) if goals_json else None
            return finance_tools.create_budget(income, expenses, goals)
        
        # Financial Metrics Calculator
        @FunctionTool
        def calculate_financial_metrics(
            data_json: str,
            metrics_json: str
        ) -> dict:
            """
            Calculate various financial metrics like ROI, savings rate, debt-to-income ratio.
            
            Args:
                data_json: JSON string of financial data with relevant values (e.g., '{"initial_investment": 10000, "current_value": 12000}')
                metrics_json: JSON string array of metrics to calculate (e.g., '["roi", "savings_rate", "debt_to_income"]')
                
            Returns:
                Calculated metrics with explanations
            """
            import json
            data = json.loads(data_json)
            metrics = json.loads(metrics_json)
            return finance_tools.calculate_financial_metrics(data, metrics)
        
        # Expense Forecasting Tool
        @FunctionTool
        def forecast_expenses(
            historical_data_json: str,
            months_ahead: int = 3
        ) -> dict:
            """
            Forecast future expenses based on historical spending patterns.
            
            Args:
                historical_data_json: JSON string array of historical expense data by month (e.g., '[{"month": "Jan", "amount": 1000}, {"month": "Feb", "amount": 1100}]')
                months_ahead: Number of months to forecast (default: 3)
                
            Returns:
                Forecasted expenses with confidence intervals and trends
            """
            import json
            historical_data = json.loads(historical_data_json)
            return finance_tools.forecast_expenses(historical_data, months_ahead)
        
        # Financial Report Generation Tool
        @FunctionTool
        def generate_financial_report(
            data_json: str,
            report_type: str = "comprehensive"
        ) -> dict:
            """
            Generate a comprehensive financial report in PDF format.
            
            Args:
                data_json: JSON string of financial data to include in the report (e.g., '{"income": 5000, "expenses": 3000}')
                report_type: Type of report ('comprehensive', 'summary', 'investment', 'budget')
                
            Returns:
                Report metadata and file information
            """
            import json
            data = json.loads(data_json)
            return finance_tools.generate_financial_report(data, report_type)
        
        # PDF Report Generation Tool
        @FunctionTool
        def generate_pdf_report(
            data_json: str,
            format: str = "pdf",
            output_dir: str = "/tmp"
        ) -> dict:
            """
            Generate a professional financial report payload using templates.
            
            This tool creates professionally formatted financial reports with charts and tables.
            Use this for creating comprehensive financial analysis documents.
            
            Args:
                data_json: JSON string of financial report data including:
                    - title: Report title (required)
                    - period: Reporting period (e.g., "Q4 2025")
                    - summary: Executive summary
                    - market_data: Market analysis data (object)
                    - income_statement: Income statement details
                    - balance_sheet: Balance sheet details
                    - cash_flow: Cash flow statement
                    - financial_metrics: Key financial metrics (object)
                    - analysis: Financial analysis text
                    - recommendations: Array of recommendations
                    - charts: Array of chart file paths to embed
                format: Output format hint for frontend ("pdf" or "docx")
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with structured content payload for frontend rendering
                
            Example:
                >>> data_json = '{"title": "Q4 2025 Financial Report", "period": "Q4 2025", "summary": "Strong performance...", "financial_metrics": {"roi": "15%", "savings_rate": "25%"}, "recommendations": ["Increase savings", "Diversify portfolio"]}'
                >>> result = generate_pdf_report(data_json, "pdf")
            """
            import json
            data = json.loads(data_json)
            template = get_template("finance", "financial_report")
            if not template:
                return {
                    "status": "error",
                    "message": "No financial report template available"
                }
            content = template.build_content(data)
            return {
                "status": "success",
                "render_type": "report",
                "format": format,
                "template": "financial_report",
                "content": content,
                "render_hint": "frontend"
            }
        
        # Chart Generation Tool
        @FunctionTool
        def generate_chart(
            data_json: str,
            chart_type: str,
            config_json: str = None,
            output_dir: str = "/tmp"
        ) -> dict:
            """
            Generate financial chart payloads for frontend rendering.
            
            Creates charts for financial data visualization. Charts can be embedded in reports
            or used standalone. Supports both static (PNG) and interactive (HTML) formats.
            
            Args:
                data_json: JSON string of chart data including:
                    - x: Array of x-axis values (for line, bar, scatter)
                    - y: Array of y-axis values or array of arrays for multiple series
                    - labels: Array of labels (for pie charts)
                    - values: Array of values (for pie charts)
                    - series_names: Optional array of series names for legend
                chart_type: Type of chart ('line', 'bar', 'scatter', 'pie', 'histogram', 'heatmap')
                config_json: Optional JSON string of configuration:
                    - title: Chart title
                    - xlabel: X-axis label
                    - ylabel: Y-axis label
                    - figsize: Array of [width, height] in inches
                    - dpi: DPI for output (default: 300)
                    - color: Color or array of colors
                    - grid: Show grid (default: true)
                    - interactive: Use plotly for interactive charts (default: false)
                output_dir: Ignored (kept for backward compatibility)
                
            Returns:
                Dictionary with chart payload for frontend rendering
                
            Example:
                >>> # Line chart for stock prices
                >>> data_json = '{"x": ["Jan", "Feb", "Mar"], "y": [100, 120, 115]}'
                >>> config_json = '{"title": "Stock Price Trend", "xlabel": "Month", "ylabel": "Price ($)"}'
                >>> result = generate_chart(data_json, "line", config_json)
                
                >>> # Pie chart for expense breakdown
                >>> data_json = '{"labels": ["Housing", "Food", "Transport"], "values": [1200, 400, 300]}'
                >>> config_json = '{"title": "Monthly Expenses"}'
                >>> result = generate_chart(data_json, "pie", config_json)
            """
            import json
            data = json.loads(data_json)
            config = json.loads(config_json) if config_json else {}
            return {
                "status": "success",
                "render_type": "chart",
                "chart_type": chart_type,
                "data": data,
                "config": config,
                "render_hint": "frontend"
            }
        
        tools.extend([
            fetch_market_data,
            analyze_bank_statement,
            create_budget,
            calculate_financial_metrics,
            forecast_expenses,
            generate_financial_report,
            generate_pdf_report,
            generate_chart
        ])
        
        return tools
