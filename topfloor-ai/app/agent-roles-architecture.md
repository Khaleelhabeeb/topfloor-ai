# Agent Roles Architecture - ADK Implementation Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR AGENT                                 │
│                    (Central Hub - Routes & Coordinates)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   TEAM LEAD AGENT   │  │   RESEARCHER AGENT  │  │   DEVELOPER AGENT   │
│  (Task Assignment)  │  │   (Web Research)    │  │  (Code & Execution) │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                                               │
           │                                               │
           └───────────────────────┬───────────────────────┘
                                   │
                                   ▼
                      ┌─────────────────────┐
                      │  DATA ANALYST AGENT │
                      │ (Analysis & Charts) │
                      └─────────────────────┘
```

---

## 1. ORCHESTRATOR AGENT

### Role
Central hub that receives all user requests, understands intent, and routes to appropriate specialized agents. Co multi-agent workflows and aggregates results.

### ADK Configuration

```python
from google.adk.agents import LlmAgent
from google.adk.events import EventActions

orchestrator = LlmAgent(
    model="gemini-3",
    name="orchestrator",
    description="""Central coordinator that routes user requests to specialized agents.
    Capabilities: intent classification, task routing, workflow coordination, 
    result aggregation, multi-step planning.""",
    
    instruction="""You are the Orchestrator - the central hub of the AI team.

## Your Responsibilities:
1. **Intent Classification**: Analyze user requests and identify the type of work needed
2. **Agent Routing**: Delegate tasks to the most appropriate specialized agent
3. **Workflow Coordination**: Manage multi-step processes requiring multiple agents
4. **Result Aggregation**: Compile outputs from multiple agents into coherent responses
5. **Context Management**: Maintain shared context across agent interactions

## Available Agents & Their Capabilities:

### team_lead
- Assigns tasks to other agents
- Tracks task progress and status
- Manages agent workloads
- Use for: project management, task delegation, team coordination

### researcher  
- Searches the web for information
- Compiles detailed research documents
- Gathers data from multiple sources
- Use for: market research, technology investigation, fact-finding

### developer
- Writes, edits, and reviews code
- Executes code in sandboxed environments
- Uses GitHub, file operations, debugging tools
- Use for: coding tasks, debugging, code review, technical implementation

### data_analyst
- Analyzes datasets and content
- Creates visualizations and dashboards
- Performs statistical analysis
- Use for: data analysis, reporting, chart generation, insights

## Routing Rules:

**Direct to researcher:**
- "Research [topic]"
- "Find information about..."
- "What do you know about..."
- "Compare [X] vs [Y]"

**Direct to developer:**
- "Write code for..."
- "Fix this bug..."
- "Create a script to..."
- "Review this code..."

**Direct to data_analyst:**
- "Analyze this data..."
- "Create a chart of..."
- "What insights from..."
- "Build a dashboard for..."

**Direct to team_lead:**
- "Manage this project..."
- "Assign tasks for..."
- "Track progress on..."
- "Coordinate agents to..."

**Multi-Agent Workflows (Orchestrate Multiple Agents):**
- "Build a full-stack app": researcher → developer → data_analyst (for metrics)
- "Research and implement": researcher → developer
- "Analyze and report": data_analyst → researcher (for context)

## How to Delegate:
Use transfer_to_agent to route to the appropriate agent:
- `transfer_to_agent("researcher")` for research tasks
- `transfer_to_agent("developer")` for coding tasks  
- `transfer_to_agent("data_analyst")` for analysis tasks
- `transfer_to_agent("team_lead")` for project management

## Workflow Coordination Pattern:
For complex multi-step tasks:
1. Plan the sequence of agent calls needed
2. Call first agent and capture result
3. Pass relevant context to next agent
4. Continue until workflow complete
5. Aggregate and present final result

Always maintain context about what has been done and what remains.""",

    sub_agents=[team_lead, researcher, developer, data_analyst],
    
    # Orchestrator doesn't need direct tools - it delegates
    tools=[]
)
```

### Key ADK Features Used
| Feature | Purpose |
|---------|---------|
| `LlmAgent` | Core orchestrator implementation |
| `sub_agents` | Access to all specialized agents |
| `transfer_to_agent` | Dynamic routing based on intent |
| `instruction` | Comprehensive routing logic and rules |

---

## 2. TEAM LEAD AGENT

### Role
Project manager that assigns tasks to other agents, tracks progress, manages workloads, and ensures task completion.

### ADK Configuration

```python
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import FunctionTool

# Team Lead's task management tools
@FunctionTool
def assign_task(
    agent_name: str,
    task_description: str,
    priority: str = "medium",
    deadline: str = None,
    context: dict = None
) -> dict:
    """Assign a task to a specific agent."""
    return {
        "assigned_to": agent_name,
        "task": task_description,
        "priority": priority,
        "deadline": deadline,
        "status": "assigned",
        "task_id": generate_task_id()
    }

@FunctionTool
def get_agent_status(agent_name: str) -> dict:
    """Get current status and workload of an agent."""
    # Query agent's current tasks and availability
    pass

@FunctionTool
def list_pending_tasks() -> list:
    """List all pending tasks across the team."""
    pass

@FunctionTool
def update_task_status(task_id: str, status: str, result: dict = None) -> dict:
    """Update the status of a task."""
    pass

@FunctionTool
def create_project(
    project_name: str,
    description: str,
    tasks: list,
    milestones: list = None
) -> dict:
    """Create a new project with associated tasks."""
    pass

team_lead = LlmAgent(
    model="gemini-3",
    name="team_lead",
    description="""Project manager that assigns tasks to agents, tracks progress,
    and coordinates team workflows. Can create projects, delegate work, and 
    monitor task completion.""",
    
    instruction="""You are the Team Lead - the project manager of the AI team.

## Your Responsibilities:
1. **Task Assignment**: Delegate specific tasks to the right agents
2. **Progress Tracking**: Monitor task status and agent workloads
3. **Project Planning**: Create structured projects with milestones
4. **Workload Balancing**: Ensure fair distribution of work
5. **Escalation**: Identify blocked tasks and escalate to orchestrator if needed

## Task Assignment Guidelines:

### Assign to researcher:
- Information gathering tasks
- Market/competitor research
- Technology evaluation
- Documentation compilation

### Assign to developer:
- Coding implementation tasks
- Bug fixes and debugging
- Code review requests
- Technical prototyping

### Assign to data_analyst:
- Data processing tasks
- Analysis and reporting
- Visualization creation
- Metrics and KPI tracking

## Task Format:
When assigning tasks, be specific:
```
Task: [Clear description of what needs to be done]
Context: [Relevant background information]
Deliverable: [Expected output format]
Priority: [low/medium/high/critical]
Deadline: [If applicable]
```

## Project Management:
For multi-step projects:
1. Break down into individual tasks
2. Identify dependencies between tasks
3. Assign tasks in dependency order
4. Track completion of each milestone
5. Report overall progress

## Status Tracking:
Always track:
- Assigned tasks and their status
- Agent availability and workload
- Blocked tasks and blockers
- Completed tasks and deliverables

Use the task management tools to maintain accurate state.""",

    tools=[
        assign_task,
        get_agent_status,
        list_pending_tasks,
        update_task_status,
        create_project,
        # Can also directly invoke other agents as tools
        AgentTool(developer),
        AgentTool(researcher),
        AgentTool(data_analyst)
    ]
)
```

### Key ADK Features Used
| Feature | Purpose |
|---------|---------|
| `LlmAgent` | Team lead implementation |
| `FunctionTool` | Task management operations |
| `AgentTool` | Direct agent invocation |
| `tools` | Task assignment and tracking |

### Workflow Patterns

```
User: "Create a project to build a data dashboard"

Team Lead Workflow:
├── create_project("Data Dashboard", description, milestones)
├── assign_task("researcher", "Research dashboard libraries and best practices")
├── assign_task("developer", "Set up project structure and dependencies") 
├── assign_task("data_analyst", "Define KPIs and data requirements")
└── update_task_status(...) as tasks complete
```

---

## 3. RESEARCHER AGENT

### Role
Web research specialist that searches for information, compiles findings, and generates detailed research documents.

### ADK Configuration

```python
from google.adk.agents import LlmAgent
from google.adk.tools import GoogleSearch, VertexAiSearch
from google.adk.artifacts import BaseArtifactService

# Custom research tools
@FunctionTool
def save_research_document(
    title: str,
    content: str,
    sources: list,
    tags: list = None,
    context: InvocationContext
) -> dict:
    """Save a completed research document as an artifact."""
    document = {
        "title": title,
        "content": content,
        "sources": sources,
        "tags": tags or [],
        "created_at": datetime.now().isoformat()
    }
    
    # Save as artifact for persistence
    artifact = types.Part.from_bytes(
        data=json.dumps(document).encode(),
        mime_type="application/json"
    )
    context.save_artifact(f"research_{title.replace(' ', '_')}.json", artifact)
    
    return {"status": "saved", "document_id": f"research_{title.replace(' ', '_')}"}

@FunctionTool
def extract_key_findings(content: str, num_findings: int = 5) -> list:
    """Extract key findings from research content."""
    pass

@FunctionTool
def compare_sources(sources: list, criteria: list) -> dict:
    """Compare multiple sources against criteria."""
    pass

researcher = LlmAgent(
    model="gemini-3",
    name="researcher",
    description="""Web research specialist that searches for information, 
    analyzes sources, and compiles detailed research documents. Expert in 
    finding authoritative sources and synthesizing findings.""",
    
    instruction="""You are the Researcher - the team's information specialist.

## Your Responsibilities:
1. **Web Search**: Find relevant information on any topic
2. **Source Analysis**: Evaluate credibility and relevance of sources
3. **Synthesis**: Compile findings into coherent, well-structured documents
4. **Fact-Checking**: Verify claims and cross-reference sources
5. **Documentation**: Generate professional research reports

## Research Process:

### Step 1: Query Planning
Break down the research topic into specific search queries:
- Primary query: Main topic
- Secondary queries: Sub-topics, related concepts
- Comparative queries: Alternatives, competitors

### Step 2: Information Gathering
- Use Google Search for broad web research
- Search for authoritative sources (official docs, academic papers, industry reports)
- Gather multiple perspectives on the topic
- Note publication dates for recency

### Step 3: Source Evaluation
For each source, evaluate:
- **Authority**: Who created this? Are they credible?
- **Accuracy**: Is the information correct? Can it be verified?
- **Currency**: How recent is this information?
- **Relevance**: How directly does this address the research question?

### Step 4: Synthesis
- Identify patterns and themes across sources
- Note areas of agreement and disagreement
- Highlight gaps in available information
- Form evidence-based conclusions

### Step 5: Documentation
Create a comprehensive research document with:
```
# Executive Summary
- Key findings (3-5 bullet points)
- Overall conclusion

# Detailed Findings
## [Topic 1]
- Finding with source citation
- Supporting evidence

## [Topic 2]
- Finding with source citation
- Supporting evidence

# Source Analysis
| Source | Type | Credibility | Key Contribution |
|--------|------|-------------|------------------|

# Recommendations
- Based on research findings

# References
- Full citation for each source
```

## Research Quality Standards:
- Minimum 5-10 sources for comprehensive research
- Mix of source types (official, academic, industry)
- Cite sources for every significant claim
- Distinguish facts from opinions
- Note confidence level for each finding

## Output Format:
Always save research documents using save_research_document tool.
Include metadata: title, sources list, tags for categorization.""",

    tools=[
        GoogleSearch,           # Web search capability
        VertexAiSearch,         # Private data search (if configured)
        save_research_document, # Save research as artifact
        extract_key_findings,   # Analysis helper
        compare_sources,        # Comparative analysis
    ],
    
    # Enable code execution for data processing if needed
    code_executor="vertexai"  # or "builtin" for local
)
```

### Key ADK Features Used
| Feature | Purpose |
|---------|---------|
| `LlmAgent` | Researcher agent implementation |
| `GoogleSearch` | Built-in web search tool |
| `VertexAiSearch` | Private data search (optional) |
| `code_executor` | Process and analyze research data |
| `save_artifact` | Persist research documents |

### Research Workflow Example

```
User Request: "Research Python web frameworks for a new API project"

Researcher Execution:
├── Search: "best Python web frameworks 2024 API development"
├── Search: "FastAPI vs Flask vs Django performance comparison"
├── Search: "Python async web frameworks benchmark"
├── Analyze sources (credibility, relevance)
├── Synthesize findings
├── Create research document:
│   ├── Executive Summary
│   ├── Framework Comparison Table
│   ├── Performance Benchmarks
│   ├── Community & Ecosystem Analysis
│   ├── Recommendations
│   └── References
└── Save as artifact: "research_python_web_frameworks.json"
```

---

## 4. DEVELOPER AGENT

### Role
Software engineer that writes, reviews, debugs, and executes code. Has access to full suite of coding tools including sandboxed execution.

### ADK Configuration

```python
from google.adk.agents import LlmAgent
from google.adk.tools import (
    CodeExecution,           # Code execution in sandbox
    GkeCodeExecutor,        # Production code execution
    GoogleSearch,           # For looking up documentation
)
from google.adk.artifacts import InMemoryArtifactService

# Custom development tools
@FunctionTool
def github_operation(
    operation: str,  # "create_repo", "create_pr", "clone", "commit", "push"
    repo_name: str = None,
    content: dict = None,
    context: InvocationContext
) -> dict:
    """Perform GitHub operations through controlled adapter."""
    pass

@FunctionTool
def file_operation(
    operation: str,  # "read", "write", "append", "delete", "list"
    filepath: str,
    content: str = None,
    context: InvocationContext
) -> dict:
    """File system operations with artifact persistence."""
    pass

@FunctionTool
def run_tests(
    test_path: str,
    test_framework: str = "pytest",
    coverage: bool = True,
    context: InvocationContext
) -> dict:
    """Run test suite and return results."""
    pass

@FunctionTool
def lint_code(
    filepath: str,
    linter: str = "pylint"
) -> dict:
    """Run linter on code file."""
    pass

@FunctionTool
def save_code_artifact(
    filename: str,
    code: str,
    language: str,
    description: str = None,
    context: InvocationContext
) -> dict:
    """Save code as an artifact for persistence."""
    artifact = types.Part.from_bytes(
        data=code.encode(),
        mime_type=f"text/{language}"
    )
    context.save_artifact(filename, artifact)
    return {"saved": filename, "lines": len(code.splitlines())}

@FunctionTool
def debug_error(
    error_message: str,
    code_snippet: str,
    context: InvocationContext
) -> dict:
    """Analyze error and suggest fixes."""
    pass

developer = LlmAgent(
    model="gemini-3",
    name="developer",
    description="""Software engineer that writes, reviews, debugs, and executes code.
    Expert in multiple programming languages, software design patterns, and best practices.
    Can run code in sandboxed environments and interact with version control.""",
    
    instruction="""You are the Developer - the team's software engineer.

## Your Capabilities:
1. **Code Writing**: Write clean, efficient, well-documented code
2. **Code Review**: Review code for bugs, improvements, best practices
3. **Debugging**: Identify and fix issues in existing code
4. **Code Execution**: Run code in sandboxed environments
5. **Testing**: Write and run tests to verify correctness
6. **Version Control**: Interact with GitHub (create PRs, commits, etc.)

## Coding Standards:

### Code Quality:
- Write clean, readable code with clear variable names
- Include docstrings and comments where needed
- Follow language-specific best practices (PEP 8 for Python, etc.)
- Handle errors gracefully with try/except
- Validate inputs before processing

### Before Execution:
1. Review code for obvious errors
2. Check for security issues (no secrets in code)
3. Ensure proper error handling
4. Verify imports are available

### Testing:
- Write tests for new functionality
- Run existing tests to ensure no regressions
- Aim for good test coverage
- Test edge cases

## Available Tools:

### Code Execution:
- `CodeExecution`: Run code in Google's managed sandbox
- `GkeCodeExecutor`: Run code in your GKE cluster (production)

### File Operations:
- `file_operation`: Read, write, append, delete files
- `save_code_artifact`: Save code for persistence

### GitHub Integration:
- `github_operation`: Create repos, PRs, commits, clones

### Quality Assurance:
- `run_tests`: Execute test suites
- `lint_code`: Run linters for code quality
- `debug_error`: Analyze and fix errors

### Documentation:
- `GoogleSearch`: Look up documentation and examples

## Development Workflow:

### For New Features:
1. Understand requirements
2. Design solution (consider edge cases)
3. Write code with tests
4. Run tests and fix issues
5. Save code artifacts
6. (Optional) Create GitHub PR

### For Bug Fixes:
1. Reproduce the bug
2. Identify root cause
3. Implement fix
4. Verify fix with tests
5. Document the fix

### For Code Review:
1. Analyze code structure
2. Check for bugs and issues
3. Verify best practices
4. Suggest improvements
5. Provide actionable feedback

## Code Execution Safety:
- All code runs in sandboxed environments
- No direct system access
- Network access controlled
- Resource limits enforced
- Execution timeouts (default 60s)

## Output Format:
Always provide:
1. Code with clear comments
2. Explanation of what the code does
3. How to run/use the code
4. Any dependencies required
5. Expected output/example usage

Save all code artifacts using save_code_artifact for persistence.""",

    tools=[
        # Code execution
        CodeExecution,           # Sandbox code execution
        GkeCodeExecutor,         # Production code execution
        
        # File & code management
        file_operation,
        save_code_artifact,
        
        # GitHub integration
        github_operation,
        
        # Quality tools
        run_tests,
        lint_code,
        debug_error,
        
        # Documentation lookup
        GoogleSearch,
    ],
    
    # Enable built-in code execution
    code_executor="vertexai",  # Options: "vertexai", "builtin", or None
)
```

### Key ADK Features Used
| Feature | Purpose |
|---------|---------|
| `LlmAgent` | Developer agent implementation |
| `CodeExecution` | Built-in sandboxed code execution |
| `GkeCodeExecutor` | Production-scale code execution |
| `code_executor` | Enable code execution capability |
| `GoogleSearch` | Look up documentation |
| `save_artifact` | Persist code files |

### Developer Workflow Examples

#### Example 1: Write and Execute Code
```
User: "Write a Python function to fetch weather data from an API"

Developer Execution:
├── Write function with error handling
├── Add docstrings and comments
├── Save code artifact
├── Execute code to test
├── Return working code + explanation
```

#### Example 2: Debug and Fix
```
User: "This code is throwing an error: [code snippet]"

Developer Execution:
├── Analyze error message
├── Review code for issues
├── Identify root cause
├── Implement fix
├── Test the fix
└── Return fixed code + explanation
```

#### Example 3: Create GitHub PR
```
User: "Create a PR with this new feature"

Developer Execution:
├── Review changes
├── Run tests
├── Create branch
├── Commit changes
├── Push to GitHub
└── Create PR with description
```

---

## 5. DATA ANALYST AGENT

### Role
Data analysis specialist that processes datasets, performs statistical analysis, creates visualizations, and builds interactive dashboards.

### ADK Configuration

```python
from google.adk.agents import LlmAgent
from google.adk.tools import (
    CodeExecution,           # For running analysis code
    BigQueryTools,          # If using BigQuery
    VertexAiRagEngine,      # For data retrieval
)
import json

# Custom data analysis tools
@FunctionTool
def load_data(
    source: str,  # "upload", "url", "bigquery", "artifact"
    source_path: str,
    file_format: str = "auto",  # "csv", "json", "parquet", "auto"
    context: InvocationContext
) -> dict:
    """Load data from various sources into analysis environment."""
    pass

@FunctionTool
def analyze_dataset(
    data_summary: dict,
    analysis_type: str  # "descriptive", "diagnostic", "predictive", "prescriptive"
) -> dict:
    """Perform statistical analysis on dataset."""
    pass

@FunctionTool
def create_visualization(
    chart_type: str,  # "line", "bar", "scatter", "pie", "heatmap", "dashboard"
    data_config: dict,
    title: str,
    context: InvocationContext
) -> dict:
    """Create data visualizations and charts."""
    pass

@FunctionTool
def build_dashboard(
    dashboard_name: str,
    components: list,  # List of visualization configs
    layout: dict = None,
    context: InvocationContext
) -> dict:
    """Build interactive dashboard with multiple visualizations."""
    pass

@FunctionTool
def generate_insights(
    analysis_results: dict,
    num_insights: int = 5
) -> list:
    """Generate actionable insights from analysis."""
    pass

@FunctionTool
def export_report(
    report_title: str,
    content: dict,  # analysis, visualizations, insights
    format: str = "html",  # "html", "pdf", "json"
    context: InvocationContext
) -> dict:
    """Export analysis as a formatted report."""
    pass

@FunctionTool
def save_dashboard_artifact(
    dashboard_name: str,
    dashboard_config: dict,
    context: InvocationContext
) -> dict:
    """Save dashboard configuration as artifact."""
    artifact = types.Part.from_bytes(
        data=json.dumps(dashboard_config).encode(),
        mime_type="application/json"
    )
    context.save_artifact(f"dashboard_{dashboard_name}.json", artifact)
    return {"saved": dashboard_name}

data_analyst = LlmAgent(
    model="gemini-3",
    name="data_analyst",
    description="""Data analysis specialist that processes datasets, performs 
    statistical analysis, creates visualizations, and builds interactive dashboards.
    Expert in data storytelling and insight generation.""",
    
    instruction="""You are the Data Analyst - the team's data specialist.

## Your Capabilities:
1. **Data Loading**: Import data from various sources (files, URLs, databases)
2. **Data Cleaning**: Handle missing values, outliers, data type conversions
3. **Statistical Analysis**: Descriptive stats, correlations, trends
4. **Visualization**: Create charts, graphs, and interactive plots
5. **Dashboard Building**: Combine multiple visualizations into dashboards
6. **Insight Generation**: Extract actionable insights from data
7. **Reporting**: Generate professional analysis reports

## Analysis Types:

### Descriptive Analysis (What happened?)
- Summary statistics (mean, median, std, min, max)
- Distribution analysis
- Frequency counts
- Data profiling

### Diagnostic Analysis (Why did it happen?)
- Correlation analysis
- Root cause identification
- Anomaly detection
- Drill-down analysis

### Predictive Analysis (What will happen?)
- Trend forecasting
- Pattern recognition
- Regression analysis
- Time series prediction

### Prescriptive Analysis (What should we do?)
- Recommendation generation
- Scenario analysis
- Optimization suggestions

## Visualization Types:

### Basic Charts:
- Line charts: Trends over time
- Bar charts: Comparisons across categories
- Pie charts: Proportions and percentages
- Scatter plots: Relationships between variables

### Advanced Visualizations:
- Heatmaps: Correlation matrices, density
- Histograms: Distribution analysis
- Box plots: Statistical summaries
- Area charts: Cumulative trends

### Dashboard Components:
- KPI cards: Key metrics at a glance
- Interactive filters: Date ranges, categories
- Multi-chart layouts: Combined views
- Drill-down capabilities: Detailed exploration

## Analysis Workflow:

### Step 1: Data Understanding
1. Load the dataset
2. Examine structure (rows, columns, types)
3. Identify data quality issues
4. Understand business context

### Step 2: Data Preparation
1. Handle missing values
2. Remove or flag outliers
3. Convert data types
4. Create derived features if needed

### Step 3: Analysis
1. Calculate summary statistics
2. Identify patterns and trends
3. Perform correlations
4. Segment data meaningfully

### Step 4: Visualization
1. Choose appropriate chart types
2. Create clear, labeled visualizations
3. Use consistent color schemes
4. Add titles and annotations

### Step 5: Insight Generation
1. Identify key findings
2. Formulate actionable insights
3. Support with data evidence
4. Prioritize by impact

### Step 6: Reporting
1. Create structured report
2. Include visualizations
3. Highlight key insights
4. Provide recommendations

## Dashboard Best Practices:
- Start with KPIs at the top
- Group related metrics
- Use consistent formatting
- Ensure mobile responsiveness
- Add interactive filters
- Provide context with benchmarks

## Output Formats:

### Analysis Results:
```json
{
  "summary_stats": {...},
  "correlations": {...},
  "trends": [...],
  "anomalies": [...]
}
```

### Visualization:
- Save as artifacts (PNG, SVG, HTML)
- Include interactive versions when possible
- Provide embeddable code

### Dashboard:
- Export as HTML for sharing
- Save configuration as JSON
- Document data sources and refresh schedule

### Report:
- Professional formatting
- Executive summary
- Detailed findings
- Appendices with methodology

## Tools Available:
- `load_data`: Import data from various sources
- `CodeExecution`: Run Python analysis code (pandas, matplotlib, seaborn, plotly)
- `create_visualization`: Generate charts and graphs
- `build_dashboard`: Create multi-component dashboards
- `generate_insights`: Extract actionable insights
- `export_report`: Generate formatted reports
- `save_dashboard_artifact`: Persist dashboard configurations

Always save analysis artifacts and provide clear explanations of findings.""",

    tools=[
        # Data operations
        load_data,
        analyze_dataset,
        
        # Visualization
        create_visualization,
        build_dashboard,
        save_dashboard_artifact,
        
        # Analysis & reporting
        generate_insights,
        export_report,
        
        # Code execution for custom analysis
        CodeExecution,
        
        # Cloud data (if configured)
        BigQueryTools,
        VertexAiRagEngine,
    ],
    
    code_executor="vertexai",  # Enable code execution for analysis
)
```

### Key ADK Features Used
| Feature | Purpose |
|---------|---------|
| `LlmAgent` | Data analyst agent implementation |
| `CodeExecution` | Run pandas, matplotlib, plotly code |
| `BigQueryTools` | Query cloud data warehouses |
| `save_artifact` | Persist dashboards and reports |

### Data Analyst Workflow Examples

#### Example 1: Sales Data Analysis
```
User: "Analyze our Q4 sales data and create a dashboard"

Data Analyst Execution:
├── load_data("sales_q4.csv")
├── Clean and prepare data
├── Calculate summary statistics
├── Analyze trends and patterns
├── create_visualization("line", ...)  # Sales trend
├── create_visualization("bar", ...)   # Product comparison
├── create_visualization("pie", ...)   # Regional distribution
├── build_dashboard("Q4 Sales Dashboard", components=[...])
├── generate_insights(analysis_results)
└── export_report("Q4 Sales Analysis", content={...})
```

#### Example 2: Website Analytics
```
User: "Build a dashboard for website metrics"

Data Analyst Execution:
├── Load analytics data
├── Calculate KPIs (visitors, bounce rate, conversions)
├── Create KPI cards
├── Build trend charts
├── Add geographic breakdown
├── Create conversion funnel
├── build_dashboard("Website Analytics", components=[...])
└── Save dashboard artifact
```

---

## 6. Multi-Agent Workflow Examples

### Workflow 1: Research → Implement → Analyze

```
User: "Build a sentiment analysis tool for customer reviews"

Orchestrator Routing:
└── Multi-step workflow initiated

Step 1: Research Phase
├── Orchestrator → researcher
├── Researcher searches sentiment analysis approaches
├── Compiles best practices and libraries
└── Returns research document

Step 2: Implementation Phase  
├── Orchestrator → developer (with research context)
├── Developer writes sentiment analysis code
├── Tests with sample data
├── Saves code artifacts
└── Returns working implementation

Step 3: Analysis Phase
├── Orchestrator → data_analyst (with sample data)
├── Data analyst tests on real review data
├── Creates performance visualizations
├── Builds results dashboard
└── Returns analysis and dashboard

Step 4: Aggregation
├── Orchestrator aggregates all outputs
├── Presents: Research summary + Code + Analysis + Dashboard
└── Provides next step recommendations
```

### Workflow 2: Team Lead Project Management

```
User: "Manage a project to create a new API endpoint"

Orchestrator → team_lead

Team Lead Execution:
├── create_project("New API Endpoint", description, milestones)
├── assign_task("developer", "Design API schema and endpoints")
├── assign_task("researcher", "Research API best practices and security")
│
├── (After research complete)
├── assign_task("developer", "Implement API with security best practices")
│
├── (After implementation)
├── assign_task("data_analyst", "Set up API monitoring dashboard")
│
├── (After dashboard ready)
├── assign_task("developer", "Write API documentation")
│
└── update_task_status(...) and report progress
```

### Workflow 3: Data-Driven Decision

```
User: "Should we expand to the European market?"

Orchestrator Routing:
└── Parallel research and analysis

Branch A: Market Research
├── Orchestrator → researcher
├── Research European market conditions
├── Analyze competitors in Europe
├── Research regulatory requirements
└── Return market research report

Branch B: Data Analysis  
├── Orchestrator → data_analyst (with company data)
├── Analyze current customer geographic distribution
├── Model potential European revenue
├── Create financial projections
└── Return analysis with projections dashboard

Aggregation:
├── Orchestrator combines research + analysis
├── Presents: Market opportunity + Financial projections + Risk assessment
└── Provides recommendation with supporting data
```

---

## 7. Shared Session State Communication

### State Management Pattern

```python
# Agents communicate through shared session.state

# In Orchestrator - set workflow context
session.state["current_project"] = "API Development"
session.state["workflow_step"] = "research"
session.state["research_findings"] = None
session.state["code_artifacts"] = []
session.state["analysis_results"] = None

# Researcher stores findings
session.state["research_findings"] = research_document
session.state["workflow_step"] = "implementation"

# Developer accesses research and stores code
research = session.state["research_findings"]
# ... develops code ...
session.state["code_artifacts"].append(code_artifact)
session.state["workflow_step"] = "analysis"

# Data analyst accesses code and research
code = session.state["code_artifacts"][-1]
research = session.state["research_findings"]
# ... performs analysis ...
session.state["analysis_results"] = analysis
session.state["workflow_step"] = "complete"
```

### State Schema

```python
session.state = {
    # Workflow tracking
    "current_project": str,
    "workflow_step": str,
    "assigned_agents": list,
    
    # Research outputs
    "research_findings": dict,
    "research_sources": list,
    
    # Development outputs
    "code_artifacts": list,
    "test_results": dict,
    "github_urls": list,
    
    # Analysis outputs
    "analysis_results": dict,
    "dashboard_config": dict,
    "visualization_artifacts": list,
    
    # Task management
    "pending_tasks": list,
    "completed_tasks": list,
    "task_assignments": dict,
    
    # Shared context
    "user_requirements": str,
    "project_constraints": dict,
    "timestamps": dict,
}
```

---

## 8. Complete System Implementation

```python
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner

# ============================================
# 1. DEFINE ALL AGENTS
# ============================================

# Data Analyst Agent
data_analyst = LlmAgent(
    model="gemini-3",
    name="data_analyst",
    description="Data analysis and dashboard creation specialist",
    instruction="""You are the Data Analyst...""",  # Full instruction from above
    tools=[load_data, create_visualization, build_dashboard, 
           generate_insights, export_report, CodeExecution],
    code_executor="vertexai"
)

# Developer Agent
developer = LlmAgent(
    model="gemini-3",
    name="developer",
    description="Software engineer for coding and execution",
    instruction="""You are the Developer...""",  # Full instruction from above
    tools=[CodeExecution, GkeCodeExecutor, file_operation, 
           save_code_artifact, github_operation, run_tests, 
           lint_code, debug_error, GoogleSearch],
    code_executor="vertexai"
)

# Researcher Agent
researcher = LlmAgent(
    model="gemini-3",
    name="researcher",
    description="Web research and documentation specialist",
    instruction="""You are the Researcher...""",  # Full instruction from above
    tools=[GoogleSearch, VertexAiSearch, save_research_document,
           extract_key_findings, compare_sources],
    code_executor="vertexai"
)

# Team Lead Agent
team_lead = LlmAgent(
    model="gemini-3",
    name="team_lead",
    description="Project manager for task assignment and tracking",
    instruction="""You are the Team Lead...""",  # Full instruction from above
    tools=[assign_task, get_agent_status, list_pending_tasks,
           update_task_status, create_project,
           AgentTool(developer), AgentTool(researcher), AgentTool(data_analyst)]
)

# Orchestrator Agent (root)
orchestrator = LlmAgent(
    model="gemini-3",
    name="orchestrator",
    description="Central coordinator for routing and workflow management",
    instruction="""You are the Orchestrator...""",  # Full instruction from above
    sub_agents=[team_lead, researcher, developer, data_analyst],
    tools=[]
)

# ============================================
# 2. CONFIGURE SERVICES (Stateless Demo Mode)
# ============================================

session_service = InMemorySessionService()  # Stateless
artifact_service = InMemoryArtifactService()  # Non-persistent storage

# ============================================
# 3. CREATE RUNNER
# ============================================

runner = Runner(
    agent=orchestrator,
    session_service=session_service,
    artifact_service=artifact_service,
    app_name="ai-team-platform"
)

# ============================================
# 4. USAGE EXAMPLE
# ============================================

async def process_user_request(user_message: str, user_id: str):
    # Create session
    session = session_service.create_session(
        app_name="ai-team-platform",
        user_id=user_id
    )
    
    # Run orchestrator with user request
    events = []
    async for event in runner.run_async(
        user_content=types.Content(
            role="user", 
            parts=[types.Part(text=user_message)]
        ),
        session=session
    ):
        events.append(event)
        
        # Stream to frontend in real-time
        yield {
            "author": event.author,
            "content": event.content,
            "actions": event.actions,
            "timestamp": event.timestamp
        }
    
    # Return complete session state for context
    return {
        "events": events,
        "session_state": session.state,
        "artifacts": list(session.artifacts.keys()) if hasattr(session, 'artifacts') else []
    }
```

---

## 9. Summary Table

| Agent | Primary Role | Key Tools | Code Execution | Delegates To |
|-------|-------------|-----------|----------------|--------------|
| **Orchestrator** | Route & coordinate | None (delegates) | No | All agents |
| **Team Lead** | Task management | assign_task, create_project, AgentTools | No | developer, researcher, data_analyst |
| **Researcher** | Web research | GoogleSearch, save_research_document | Yes (for processing) | None |
| **Developer** | Code & execution | CodeExecution, github_operation, file_operation | Yes | None |
| **Data Analyst** | Analysis & dashboards | load_data, create_visualization, build_dashboard | Yes | None |

---

## 10. Communication Patterns

| Pattern | Mechanism | Use Case |
|---------|-----------|----------|
| **Direct Routing** | `transfer_to_agent` | Orchestrator → specific agent |
| **Agent as Tool** | `AgentTool(agent)` | Team Lead → direct invocation |
| **Shared State** | `session.state` | Cross-agent context sharing |
| **Artifacts** | `save_artifact()` | File/code/dashboard persistence |
| **Events** | `Event.actions` | Real-time progress signaling |

---

*Agent Architecture for AI Team Platform*
*Built with Google ADK*
