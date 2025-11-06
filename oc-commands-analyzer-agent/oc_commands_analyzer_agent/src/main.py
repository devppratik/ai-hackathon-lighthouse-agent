"""Main entry point for the OC Commands Analyzer Agent."""

import sys

import uvicorn

from oc_commands_analyzer_agent.src.api import app
from oc_commands_analyzer_agent.src.settings import settings, validate_config
from oc_commands_analyzer_agent.utils.pylogger import (
    get_python_logger,
    get_uvicorn_log_config,
)

logger = get_python_logger()


def main() -> None:
    """Main entry point for the agent."""
    try:
        # Validate configuration
        validate_config(settings)

        logger.info(
            f"Starting OC Commands Analyzer Agent with {settings.LLM_PROVIDER} provider"
        )
        logger.info(f"MCP Server URL: {settings.MCP_SERVER_URL}")
        logger.info(f"Checkpointing: {'enabled' if settings.USE_CHECKPOINTING else 'disabled'}")

        # Run the server
        uvicorn.run(
            app,
            host=settings.AGENT_HOST,
            port=settings.AGENT_PORT,
            log_config=get_uvicorn_log_config(settings.PYTHON_LOG_LEVEL),
        )

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        logger.critical(f"Failed to start agent: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("OC Commands Analyzer Agent shutting down")


if __name__ == "__main__":
    main()
