"""OC Commands Analyzer MCP Server implementation.

This module contains the main OC Commands Analyzer MCP Server class that provides
tools for analyzing OpenShift CLI commands.
"""

from fastmcp import FastMCP

from oc_commands_analyzer_mcp_server.src.settings import settings

# Import tools from the tools package
from oc_commands_analyzer_mcp_server.src.tools.oc_analyzer_tool import (
    analyze_oc_command,
    explain_oc_resource,
    get_oc_help,
)
from oc_commands_analyzer_mcp_server.utils.pylogger import (
    force_reconfigure_all_loggers,
    get_python_logger,
)

logger = get_python_logger()


class OCCommandsAnalyzerMCPServer:
    """Main OC Commands Analyzer MCP Server implementation.

    This server provides tools for analyzing OpenShift CLI (oc) commands,
    following the tools-first architectural pattern for MCP servers.
    """

    def __init__(self):
        """Initialize the MCP server with OC analysis tools."""
        try:
            # Initialize FastMCP server
            self.mcp = FastMCP("oc-commands-analyzer")

            # Force reconfigure all loggers after FastMCP initialization
            force_reconfigure_all_loggers(settings.PYTHON_LOG_LEVEL)

            self._register_mcp_tools()

            logger.info("OC Commands Analyzer MCP Server initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OC Commands Analyzer MCP Server: {e}")
            raise

    def _register_mcp_tools(self) -> None:
        """Register MCP tools for OC command analysis.

        Registers all available tools with the FastMCP server instance.
        Currently includes:
        - analyze_oc_command: Parse and analyze oc command syntax and semantics
        - get_oc_help: Retrieve help documentation for oc commands
        - explain_oc_resource: Get detailed documentation about OpenShift resources
        """
        # Register all the imported tools
        self.mcp.tool()(analyze_oc_command)
        self.mcp.tool()(get_oc_help)
        self.mcp.tool()(explain_oc_resource)
