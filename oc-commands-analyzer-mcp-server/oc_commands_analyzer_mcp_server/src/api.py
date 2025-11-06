"""This module sets up the FastAPI application for the OC Commands Analyzer MCP server.

It initializes the FastAPI app and sets up the MCP server with appropriate transport protocols.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from oc_commands_analyzer_mcp_server.src.mcp import OCCommandsAnalyzerMCPServer
from oc_commands_analyzer_mcp_server.src.settings import settings
from oc_commands_analyzer_mcp_server.utils.pylogger import get_python_logger

logger = get_python_logger(settings.PYTHON_LOG_LEVEL)

server = OCCommandsAnalyzerMCPServer()

# Choose the appropriate transport protocol based on settings
if settings.MCP_TRANSPORT_PROTOCOL == "sse":
    from fastmcp.server.http import create_sse_app

    mcp_app = create_sse_app(server.mcp, message_path="/sse/message", sse_path="/sse")
else:  # Default to standard HTTP (works for both "http" and "streamable-http")
    mcp_app = server.mcp.http_app(path="/mcp")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan handler for MCP initialization."""
    # Run MCP lifespan
    async with mcp_app.lifespan(app):
        logger.info("OC Commands Analyzer MCP Server is ready to accept connections")
        yield

    logger.info("OC Commands Analyzer MCP Server shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint for the MCP server."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "oc-commands-analyzer-mcp-server",
            "transport_protocol": settings.MCP_TRANSPORT_PROTOCOL,
            "version": "0.1.0",
        },
    )


app.mount("/", mcp_app)
