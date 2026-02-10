from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.ws import router as ws_router
from app.api.memory import router as memory_router
from app.api.ceo import router as ceo_router
from app.api.tools import router as tools_router
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TopFloor AI - Multi-Agent Platform",
    version="1.0.0",
    description="""
    ## TopFloor AI - Gamified Multi-Agent Office Platform
    
    A comprehensive AI platform featuring specialized agents for different business functions.
    
    ### Features
    
    * **Specialized Agents** - Finance, Data Analysis, Research, Team Lead
    * **Real-Time Chat** - WebSocket support for streaming responses
    * **Background Tasks** - Asynchronous task processing with queue management
    * **Long-Term Memory** - Vector database for contextual memory
    * **Report Payloads** - Structured JSON for frontend rendering
    * **Secure & Private** - JWT authentication with user data isolation
    
    ### Available Agents
    
    * **Finance Agent** - Market analysis, budgeting, expense tracking
    * **Data Analyst** - Data visualization, statistical analysis, reporting
    * **Researcher** - Web research, information gathering, source verification
    * **Team Lead** - Task coordination and multi-agent orchestration
    * **Orchestrator** - Intelligent request routing
    
    ### Getting Started
    
    1. Register an account: `POST /api/v1/auth/register`
    2. Login to get JWT token: `POST /api/v1/auth/login`
    3. Use token in Authorization header: `Bearer <token>`
    4. Start chatting with agents or create tasks!
    
    ### Documentation
    
    * **API Reference**: See endpoints below
    * **User Guides**: Check `/docs` folder in repository
    * **GitHub**: [github.com/yourusername/topfloor-ai](https://github.com/yourusername/topfloor-ai)
    
    ### Support
    
    * **Issues**: Report bugs on GitHub
    * **Email**: support@topfloor-ai.com
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "TopFloor AI Support",
        "email": "support@topfloor-ai.com",
        "url": "https://github.com/yourusername/topfloor-ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management"
        },
        {
            "name": "Agents",
            "description": "Interact with specialized AI agents"
        },
        {
            "name": "Tasks",
            "description": "Create and manage background tasks"
        },
        {
            "name": "Memory",
            "description": "Long-term memory storage and retrieval"
        },
        {
            "name": "WebSocket",
            "description": "Real-time communication with agents"
        },
        {
            "name": "CEO",
            "description": "CEO dashboard endpoints"
        },
        {
            "name": "Tools",
            "description": "Utility endpoints"
        },
        {
            "name": "Health",
            "description": "System health and status checks"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return more informative error for debugging
    error_msg = str(exc)
    if "quota" in error_msg.lower() or "429" in error_msg:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "API rate limit exceeded. Please try again later or check your API key quota."}
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An internal server error occurred: {error_msg}"}
    )

# Include routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(ceo_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint - Welcome message and quick links
    
    Returns basic information about the API and links to documentation.
    """
    return {
        "message": "Welcome to TopFloor AI - Multi-Agent Platform",
        "version": "1.0.0",
        "status": "healthy",
        "description": "AI-powered platform with specialized agents for finance, data analysis, and research",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "github": "https://github.com/yourusername/topfloor-ai"
        },
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "agents": "/api/v1/agents",
            "tasks": "/api/v1/tasks",
            "memory": "/api/v1/memory"
        },
        "agents": [
            {"type": "finance", "name": "Finance Agent", "description": "Financial analysis and budgeting"},
            {"type": "data_analyst", "name": "Data Analyst", "description": "Data visualization and analysis"},
            {"type": "researcher", "name": "Researcher", "description": "Web research and information gathering"},
            {"type": "team_lead", "name": "Team Lead", "description": "Task coordination and management"}
        ]
    }


@app.get("/health", tags=["Health"])
def health():
    """
    Health check endpoint
    
    Returns the health status of the API and configuration status.
    Useful for monitoring and load balancer health checks.
    """
    return {
        "status": "ok",
    }


@app.get("/api/v1/health", tags=["Health"])
def api_health():
    """
    API v1 health check
    
    Returns health status and available endpoints for API version 1.
    """
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "agents": "/api/v1/agents",
            "tasks": "/api/v1/tasks",
            "memory": "/api/v1/memory"
        }
    }


@app.get("/api/v1/memory/health", tags=["Health"])
def memory_health():
    """
    Memory system health check
    
    Verifies connection to the vector database (Chroma) and returns
    information about the memory system status.
    """
    try:
        from app.services.chroma_connection import get_chroma_client
        client = get_chroma_client()
        # Try to list collections to verify connection
        collections = client.list_collections()
        return {
            "status": "healthy",
            "chroma_connected": True,
            "collections_count": len(collections),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "chroma_connected": False,
            "error": str(e)
        }

