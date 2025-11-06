"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oc_commands_analyzer_agent.src.routes import health, stream
from oc_commands_analyzer_agent.src.settings import settings
from oc_commands_analyzer_agent.utils.pylogger import get_python_logger

logger = get_python_logger(settings.PYTHON_LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title="OC Commands Analyzer Agent",
    description="AI agent for analyzing OpenShift CLI commands",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(stream.router, prefix="/v1", tags=["Chat"])

logger.info("FastAPI application initialized")
