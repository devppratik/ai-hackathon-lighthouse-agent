"""Agent implementation for OC Commands Analyzer."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from oc_commands_analyzer_agent.src.core.prompt import get_system_prompt
from oc_commands_analyzer_agent.src.settings import settings
from oc_commands_analyzer_agent.utils.pylogger import get_python_logger

logger = get_python_logger(log_level=settings.PYTHON_LOG_LEVEL)


def get_llm_model():
    """Get the configured LLM model (Ollama or Vertex AI)."""
    if settings.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        logger.info(
            f"Initializing Ollama model: {settings.OLLAMA_MODEL} at {settings.OLLAMA_BASE_URL}"
        )
        return ChatOllama(
            model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=0.3
        )
    elif settings.LLM_PROVIDER == "vertex":
        from langchain_google_vertexai import ChatVertexAI

        # Setup Google credentials
        settings.setup_google_credentials()

        logger.info(
            f"Initializing Vertex AI model: {settings.VERTEX_MODEL} "
            f"in project {settings.VERTEX_PROJECT_ID}"
        )
        return ChatVertexAI(
            model=settings.VERTEX_MODEL,
            project=settings.VERTEX_PROJECT_ID,
            location=settings.VERTEX_LOCATION,
            temperature=0.3,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


@asynccontextmanager
async def get_oc_analyzer_agent(enable_checkpointing: bool = True):
    """Get a fully initialized OC Commands Analyzer agent.

    Args:
        enable_checkpointing: Whether to enable conversation checkpointing.

    Yields:
        The initialized agent instance.
    """
    # Initialize MCP client and get tools
    tools = []
    try:
        client = MultiServerMCPClient(
            {
                "oc-commands-analyzer": {
                    "url": settings.MCP_SERVER_URL,
                    "transport": settings.MCP_SERVER_TRANSPORT,
                },
            }
        )
        tools = await client.get_tools()
        logger.info(
            f"Successfully connected to MCP server and loaded {len(tools)} tools"
        )
    except Exception as e:
        logger.warning(f"Could not connect to MCP server: {e}")
        logger.info("Running without MCP tools - agent will have limited functionality")
        tools = []

    # Initialize the language model
    model = get_llm_model()

    # Create checkpointer if enabled
    checkpointer = None
    checkpointer_ctx = None
    if enable_checkpointing and settings.USE_CHECKPOINTING:
        # Ensure data directory exists
        db_dir = os.path.dirname(settings.SQLITE_DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Use the context manager properly
        checkpointer_ctx = AsyncSqliteSaver.from_conn_string(settings.SQLITE_DB_PATH)
        checkpointer = await checkpointer_ctx.__aenter__()
        logger.info(f"Checkpointing enabled with SQLite at {settings.SQLITE_DB_PATH}")

    # Create the agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=get_system_prompt(),
        checkpointer=checkpointer,
    )

    logger.info(
        f"OC Analyzer agent initialized with {settings.LLM_PROVIDER} "
        f"and {len(tools)} tools"
    )

    try:
        yield agent
    finally:
        # Cleanup
        if checkpointer_ctx:
            try:
                await checkpointer_ctx.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing checkpointer: {e}")
