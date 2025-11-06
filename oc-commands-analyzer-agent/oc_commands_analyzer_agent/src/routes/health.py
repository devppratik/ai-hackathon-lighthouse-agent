"""Health check route."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from oc_commands_analyzer_agent.src.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "oc-commands-analyzer-agent",
            "version": "0.1.0",
            "llm_provider": settings.LLM_PROVIDER,
            "mcp_server": settings.MCP_SERVER_URL,
        },
    )
