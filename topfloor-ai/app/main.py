from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.ws import router as ws_router
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
    description="AI-powered multi-agent system with orchestration and collaboration",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.get("/")
def root():
    """Root endpoint - basic health check"""
    return {
        "message": "TopFloor AI is up and running",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_key_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
    }


@app.get("/api/v1/health")
def api_health():
    """API v1 health check"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "agents": "/api/v1/agents",
            "tasks": "/api/v1/tasks",
        }
    }
