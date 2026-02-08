"""
Document Templates - Structured templates for each agent type

This module provides pre-defined document templates for:
- Finance Agent reports
- Data Analyst reports
- Researcher reports
- Team Lead status reports

Each template defines the structure, sections, and formatting
for professional document generation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class DocumentTemplate:
    """Base class for document templates"""
    
    def __init__(self, agent_type: str, template_name: str):
        self.agent_type = agent_type
        self.template_name = template_name
    
    def build_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build document content structure from data.
        
        Args:
            data: Input data for the document
            
        Returns:
            Structured content dictionary ready for PDF/DOCX generation
        """
        raise NotImplementedError("Subclasses must implement build_content")


class FinanceReportTemplate(DocumentTemplate):
    """Template for Finance Agent reports"""
    
    def __init__(self):
        super().__init__("finance", "financial_report")
    
    def build_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build financial report content.
        
        Expected data fields:
            - title: Report title
            - period: Reporting period (e.g., "Q4 2025")
            - summary: Executive summary
            - market_data: Market analysis data
            - income_statement: Income statement details
            - balance_sheet: Balance sheet details
            - cash_flow: Cash flow statement
            - financial_metrics: Key financial metrics
            - analysis: Financial analysis text
            - recommendations: List of recommendations
            - charts: List of chart file paths
        """
        content = {
            "title": data.get("title", "Financial Report"),
            "subtitle": data.get("period", ""),
            "author": "Finance Agent - TopFloor AI",
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "metadata": {
                "agent": "Finance Agent",
                "template": self.template_name,
                "generated_at": datetime.now().isoformat()
            },
            "sections": []
        }
        
        # Add executive summary
        if data.get("summary"):
            content["summary"] = data["summary"]
        
        # Section 1: Market Overview
        if data.get("market_data"):
            market_section = {
                "title": "Market Overview",
                "content": self._format_market_data(data["market_data"]),
                "charts": data.get("market_charts", [])
            }
            content["sections"].append(market_section)
        
        # Section 2: Financial Statements
        statements_content = []
        
        if data.get("income_statement"):
            statements_content.append("**Income Statement**\n\n" + data["income_statement"])
        
        if data.get("balance_sheet"):
            statements_content.append("**Balance Sheet**\n\n" + data["balance_sheet"])
        
        if data.get("cash_flow"):
            statements_content.append("**Cash Flow Statement**\n\n" + data["cash_flow"])
        
        if statements_content:
            content["sections"].append({
                "title": "Financial Statements",
                "content": "\n\n".join(statements_content),
                "tables": data.get("financial_tables", [])
            })
        
        # Section 3: Key Financial Metrics
        if data.get("financial_metrics"):
            metrics_section = {
                "title": "Key Financial Metrics",
                "content": self._format_metrics(data["financial_metrics"]),
                "tables": [self._build_metrics_table(data["financial_metrics"])]
            }
            content["sections"].append(metrics_section)
        
        # Section 4: Financial Analysis
        if data.get("analysis"):
            content["sections"].append({
                "title": "Financial Analysis",
                "content": data["analysis"],
                "charts": data.get("analysis_charts", [])
            })
        
        # Section 5: Recommendations
        if data.get("recommendations"):
            recommendations_text = self._format_recommendations(data["recommendations"])
            content["sections"].append({
                "title": "Recommendations",
                "content": recommendations_text
            })
        
        # Add appendix if present
        if data.get("appendix"):
            content["appendix"] = data["appendix"]
        
        return content
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data into readable text"""
        lines = []
        for symbol, info in market_data.items():
            lines.append(f"**{symbol}**")
            lines.append(f"Current Price: ${info.get('price', 'N/A')}")
            lines.append(f"Change: {info.get('change', 'N/A')} ({info.get('change_percent', 'N/A')}%)")
            lines.append(f"Volume: {info.get('volume', 'N/A')}")
            lines.append("")
        return "\n".join(lines)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format financial metrics into readable text"""
        lines = []
        for metric, value in metrics.items():
            formatted_metric = metric.replace("_", " ").title()
            lines.append(f"**{formatted_metric}:** {value}")
        return "\n\n".join(lines)
    
    def _build_metrics_table(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Build a table for financial metrics"""
        headers = ["Metric", "Value"]
        rows = []
        for metric, value in metrics.items():
            formatted_metric = metric.replace("_", " ").title()
            rows.append([formatted_metric, str(value)])
        
        return {"headers": headers, "rows": rows}
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations as a bulleted list"""
        return "\n\n".join([f"• {rec}" for rec in recommendations])


class DataAnalysisReportTemplate(DocumentTemplate):
    """Template for Data Analyst reports"""
    
    def __init__(self):
        super().__init__("data_analyst", "data_analysis_report")
    
    def build_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build data analysis report content.
        
        Expected data fields:
            - title: Report title
            - dataset_name: Name of the dataset
            - dataset_info: Dataset description and metadata
            - summary: Executive summary
            - statistics: Statistical summary
            - data_quality: Data quality assessment
            - insights: List of key insights
            - visualizations: List of visualization file paths
            - recommendations: List of recommendations
        """
        content = {
            "title": data.get("title", "Data Analysis Report"),
            "subtitle": data.get("dataset_name", ""),
            "author": "Data Analyst - TopFloor AI",
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "metadata": {
                "agent": "Data Analyst",
                "template": self.template_name,
                "generated_at": datetime.now().isoformat()
            },
            "sections": []
        }
        
        # Add executive summary
        if data.get("summary"):
            content["summary"] = data["summary"]
        
        # Section 1: Dataset Information
        if data.get("dataset_info"):
            content["sections"].append({
                "title": "Dataset Information",
                "content": data["dataset_info"],
                "tables": data.get("dataset_tables", [])
            })
        
        # Section 2: Data Quality Assessment
        if data.get("data_quality"):
            content["sections"].append({
                "title": "Data Quality Assessment",
                "content": data["data_quality"],
                "tables": data.get("quality_tables", [])
            })
        
        # Section 3: Statistical Summary
        if data.get("statistics"):
            content["sections"].append({
                "title": "Statistical Summary",
                "content": data["statistics"],
                "tables": data.get("statistics_tables", []),
                "charts": data.get("statistics_charts", [])
            })
        
        # Section 4: Data Visualizations
        if data.get("visualizations"):
            viz_content = "The following visualizations provide insights into the data patterns and trends."
            content["sections"].append({
                "title": "Data Visualizations",
                "content": viz_content,
                "charts": data["visualizations"]
            })
        
        # Section 5: Key Insights
        if data.get("insights"):
            insights_text = self._format_insights(data["insights"])
            content["sections"].append({
                "title": "Key Insights",
                "content": insights_text
            })
        
        # Section 6: Recommendations
        if data.get("recommendations"):
            recommendations_text = self._format_recommendations(data["recommendations"])
            content["sections"].append({
                "title": "Recommendations",
                "content": recommendations_text
            })
        
        # Add appendix if present
        if data.get("appendix"):
            content["appendix"] = data["appendix"]
        
        return content
    
    def _format_insights(self, insights: List[str]) -> str:
        """Format insights as numbered list"""
        return "\n\n".join([f"{i+1}. {insight}" for i, insight in enumerate(insights)])
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations as bulleted list"""
        return "\n\n".join([f"• {rec}" for rec in recommendations])


class ResearchReportTemplate(DocumentTemplate):
    """Template for Researcher reports"""
    
    def __init__(self):
        super().__init__("researcher", "research_report")
    
    def build_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build research report content.
        
        Expected data fields:
            - title: Report title
            - topic: Research topic
            - summary: Executive summary
            - background: Background information
            - methodology: Research methodology
            - findings: List of key findings
            - analysis: Detailed analysis
            - conclusions: Conclusions
            - sources: List of sources/references
            - source_credibility: Source credibility assessment
        """
        content = {
            "title": data.get("title", "Research Report"),
            "subtitle": data.get("topic", ""),
            "author": "Researcher - TopFloor AI",
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "metadata": {
                "agent": "Researcher",
                "template": self.template_name,
                "generated_at": datetime.now().isoformat()
            },
            "sections": []
        }
        
        # Add executive summary
        if data.get("summary"):
            content["summary"] = data["summary"]
        
        # Section 1: Research Topic
        if data.get("topic"):
            content["sections"].append({
                "title": "Research Topic",
                "content": data["topic"]
            })
        
        # Section 2: Background
        if data.get("background"):
            content["sections"].append({
                "title": "Background",
                "content": data["background"]
            })
        
        # Section 3: Methodology
        if data.get("methodology"):
            content["sections"].append({
                "title": "Research Methodology",
                "content": data["methodology"]
            })
        
        # Section 4: Key Findings
        if data.get("findings"):
            findings_text = self._format_findings(data["findings"])
            content["sections"].append({
                "title": "Key Findings",
                "content": findings_text
            })
        
        # Section 5: Detailed Analysis
        if data.get("analysis"):
            content["sections"].append({
                "title": "Detailed Analysis",
                "content": data["analysis"],
                "charts": data.get("analysis_charts", [])
            })
        
        # Section 6: Source Credibility
        if data.get("source_credibility"):
            content["sections"].append({
                "title": "Source Credibility Assessment",
                "content": data["source_credibility"],
                "tables": data.get("credibility_tables", [])
            })
        
        # Section 7: Conclusions
        if data.get("conclusions"):
            content["sections"].append({
                "title": "Conclusions",
                "content": data["conclusions"]
            })
        
        # Section 8: References
        if data.get("sources"):
            sources_text = self._format_sources(data["sources"])
            content["sections"].append({
                "title": "References",
                "content": sources_text
            })
        
        # Add appendix if present
        if data.get("appendix"):
            content["appendix"] = data["appendix"]
        
        return content
    
    def _format_findings(self, findings: List[str]) -> str:
        """Format findings as numbered list"""
        return "\n\n".join([f"{i+1}. {finding}" for i, finding in enumerate(findings)])
    
    def _format_sources(self, sources: List[str]) -> str:
        """Format sources as numbered list"""
        return "\n".join([f"[{i+1}] {source}" for i, source in enumerate(sources)])


class TeamLeadStatusReportTemplate(DocumentTemplate):
    """Template for Team Lead status reports"""
    
    def __init__(self):
        super().__init__("team_lead", "status_report")
    
    def build_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build team status report content.
        
        Expected data fields:
            - title: Report title
            - period: Reporting period
            - summary: Executive summary
            - team_status: Overall team status
            - agent_statuses: Dict of agent statuses
            - completed_tasks: List of completed tasks
            - in_progress_tasks: List of in-progress tasks
            - pending_tasks: List of pending tasks
            - blockers: List of blockers or issues
            - metrics: Performance metrics
        """
        content = {
            "title": data.get("title", "Team Status Report"),
            "subtitle": data.get("period", ""),
            "author": "Team Lead - TopFloor AI",
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "metadata": {
                "agent": "Team Lead",
                "template": self.template_name,
                "generated_at": datetime.now().isoformat()
            },
            "sections": []
        }
        
        # Add executive summary
        if data.get("summary"):
            content["summary"] = data["summary"]
        
        # Section 1: Team Overview
        if data.get("team_status"):
            content["sections"].append({
                "title": "Team Overview",
                "content": data["team_status"]
            })
        
        # Section 2: Agent Status
        if data.get("agent_statuses"):
            agent_status_text = self._format_agent_statuses(data["agent_statuses"])
            content["sections"].append({
                "title": "Agent Status",
                "content": agent_status_text,
                "tables": [self._build_agent_status_table(data["agent_statuses"])]
            })
        
        # Section 3: Task Summary
        task_summary_content = []
        
        if data.get("completed_tasks"):
            completed_text = f"**Completed Tasks ({len(data['completed_tasks'])})**\n\n"
            completed_text += "\n".join([f"✓ {task}" for task in data["completed_tasks"]])
            task_summary_content.append(completed_text)
        
        if data.get("in_progress_tasks"):
            in_progress_text = f"**In Progress ({len(data['in_progress_tasks'])})**\n\n"
            in_progress_text += "\n".join([f"⟳ {task}" for task in data["in_progress_tasks"]])
            task_summary_content.append(in_progress_text)
        
        if data.get("pending_tasks"):
            pending_text = f"**Pending ({len(data['pending_tasks'])})**\n\n"
            pending_text += "\n".join([f"○ {task}" for task in data["pending_tasks"]])
            task_summary_content.append(pending_text)
        
        if task_summary_content:
            content["sections"].append({
                "title": "Task Summary",
                "content": "\n\n".join(task_summary_content)
            })
        
        # Section 4: Blockers and Issues
        if data.get("blockers"):
            blockers_text = self._format_blockers(data["blockers"])
            content["sections"].append({
                "title": "Blockers and Issues",
                "content": blockers_text
            })
        
        # Section 5: Performance Metrics
        if data.get("metrics"):
            content["sections"].append({
                "title": "Performance Metrics",
                "content": self._format_metrics(data["metrics"]),
                "tables": [self._build_metrics_table(data["metrics"])],
                "charts": data.get("metrics_charts", [])
            })
        
        return content
    
    def _format_agent_statuses(self, agent_statuses: Dict[str, Any]) -> str:
        """Format agent statuses into readable text"""
        lines = []
        for agent, status in agent_statuses.items():
            agent_name = agent.replace("_", " ").title()
            lines.append(f"**{agent_name}:** {status.get('status', 'Unknown')}")
            if status.get('current_task'):
                lines.append(f"  Current Task: {status['current_task']}")
            if status.get('tasks_in_queue'):
                lines.append(f"  Tasks in Queue: {status['tasks_in_queue']}")
            lines.append("")
        return "\n".join(lines)
    
    def _build_agent_status_table(self, agent_statuses: Dict[str, Any]) -> Dict[str, Any]:
        """Build a table for agent statuses"""
        headers = ["Agent", "Status", "Current Task", "Queue Length"]
        rows = []
        for agent, status in agent_statuses.items():
            agent_name = agent.replace("_", " ").title()
            rows.append([
                agent_name,
                status.get('status', 'Unknown'),
                status.get('current_task', 'None'),
                str(status.get('tasks_in_queue', 0))
            ])
        
        return {"headers": headers, "rows": rows}
    
    def _format_blockers(self, blockers: List[str]) -> str:
        """Format blockers as bulleted list"""
        if not blockers:
            return "No blockers reported."
        return "\n\n".join([f"⚠ {blocker}" for blocker in blockers])
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into readable text"""
        lines = []
        for metric, value in metrics.items():
            formatted_metric = metric.replace("_", " ").title()
            lines.append(f"**{formatted_metric}:** {value}")
        return "\n\n".join(lines)
    
    def _build_metrics_table(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Build a table for metrics"""
        headers = ["Metric", "Value"]
        rows = []
        for metric, value in metrics.items():
            formatted_metric = metric.replace("_", " ").title()
            rows.append([formatted_metric, str(value)])
        
        return {"headers": headers, "rows": rows}


# Template registry
TEMPLATES = {
    "finance": {
        "financial_report": FinanceReportTemplate(),
    },
    "data_analyst": {
        "data_analysis_report": DataAnalysisReportTemplate(),
    },
    "researcher": {
        "research_report": ResearchReportTemplate(),
    },
    "team_lead": {
        "status_report": TeamLeadStatusReportTemplate(),
    }
}


def get_template(agent_type: str, template_name: str = None) -> Optional[DocumentTemplate]:
    """
    Get a document template for a specific agent type.
    
    Args:
        agent_type: Type of agent (finance, data_analyst, researcher, team_lead)
        template_name: Optional specific template name (uses default if not provided)
        
    Returns:
        DocumentTemplate instance or None if not found
        
    Example:
        >>> template = get_template("finance", "financial_report")
        >>> content = template.build_content(data)
    """
    if agent_type not in TEMPLATES:
        return None
    
    agent_templates = TEMPLATES[agent_type]
    
    if template_name:
        return agent_templates.get(template_name)
    else:
        # Return the first (default) template for the agent
        return next(iter(agent_templates.values()), None)


def list_templates(agent_type: str = None) -> Dict[str, List[str]]:
    """
    List available templates.
    
    Args:
        agent_type: Optional agent type to filter by
        
    Returns:
        Dictionary mapping agent types to list of template names
        
    Example:
        >>> templates = list_templates()
        >>> print(templates)
        {'finance': ['financial_report'], 'data_analyst': ['data_analysis_report'], ...}
    """
    if agent_type:
        if agent_type in TEMPLATES:
            return {agent_type: list(TEMPLATES[agent_type].keys())}
        else:
            return {}
    else:
        return {agent: list(templates.keys()) for agent, templates in TEMPLATES.items()}
