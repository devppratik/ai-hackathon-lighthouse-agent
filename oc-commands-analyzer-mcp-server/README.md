# OC Commands Analyzer MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12,3.13-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Description

A production-ready Model Context Protocol (MCP) server for analyzing OpenShift CLI (oc) commands. This server provides intelligent analysis of oc commands, helping developers understand command structure, usage patterns, and best practices without executing the commands.

The server includes three powerful MCP tools:
1. **analyze_oc_command** - Parse and analyze oc command syntax and semantics
2. **get_oc_help** - Retrieve help documentation for oc commands
3. **explain_oc_resource** - Get detailed documentation about OpenShift resource types

## Features

- **Command Analysis**: Parse oc commands to understand operations, resources, flags, and arguments
- **Best Practice Recommendations**: Get suggestions for safer and more efficient command usage
- **Help Integration**: Access oc CLI help documentation directly through the MCP interface
- **Resource Documentation**: Retrieve detailed field-level documentation for OpenShift resources
- **Safe Operation**: Tools analyze commands without executing them
- **Structured Logging**: Comprehensive JSON logging with structlog
- **Multiple Transport Protocols**: Support for HTTP, SSE, and streamable-HTTP
- **SSL/TLS Support**: Optional HTTPS configuration
- **Health Monitoring**: Built-in health check endpoints

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External Clients                         │
│  (Claude Code, LLM Clients, Custom MCP Clients)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Application Layer                      │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ Health Check │  │ MCP Protocol│  │ Transport Layer   │  │
│  │  /health     │  │  Handler    │  │ (HTTP/SSE/Stream) │  │
│  └──────────────┘  └────────────┘  └────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          OC Commands Analyzer MCP Server Core               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastMCP Instance                         │  │
│  │         (Protocol Implementation)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OC Analysis Tools                        │  │
│  │  ┌────────────────┐  ┌───────────┐  ┌─────────────┐ │  │
│  │  │ analyze_oc_    │  │ get_oc_   │  │ explain_oc_ │ │  │
│  │  │ command        │  │ help      │  │ resource    │ │  │
│  │  └────────────────┘  └───────────┘  └─────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Infrastructure Layer                           │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌──────────────┐ │  │
│  │  │ Settings     │  │ Structured │  │ Error        │ │  │
│  │  │ Management   │  │ Logging    │  │ Handling     │ │  │
│  │  └──────────────┘  └────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Code Structure

```
oc-commands-analyzer-mcp-server/
├── oc_commands_analyzer_mcp_server/    # Main package directory
│   ├── __init__.py
│   ├── src/                            # Core source code
│   │   ├── __init__.py
│   │   ├── main.py                    # Application entry point & startup logic
│   │   ├── api.py                     # FastAPI application & transport setup
│   │   ├── mcp.py                     # MCP server implementation & tool registration
│   │   ├── settings.py                # Pydantic-based configuration management
│   │   └── tools/                     # MCP tool implementations
│   │       ├── __init__.py
│   │       ├── oc_analyzer_tool.py   # OC command analysis tools
│   │       └── assets/                # Static resource files (if needed)
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       └── pylogger.py               # Structured logging with structlog
├── tests/                             # Test suite (to be added)
│   └── __init__.py
├── pyproject.toml                     # Project metadata & dependencies
├── .env.example                       # Environment configuration template
├── .gitignore                         # Version control exclusions
└── README.md                          # Project documentation
```

### Key Components

- **`main.py`**: Application entry point with configuration validation and uvicorn server startup
- **`api.py`**: FastAPI application setup with transport protocol selection and health endpoints
- **`mcp.py`**: Core MCP server class that registers OC analysis tools using FastMCP decorators
- **`settings.py`**: Environment-based configuration using Pydantic BaseSettings with validation
- **`tools/oc_analyzer_tool.py`**: Three OC command analysis tools
- **`utils/pylogger.py`**: Structured JSON logging using structlog

### MCP Tools

#### 1. analyze_oc_command

Analyzes an OpenShift CLI command to understand its structure and purpose.

**Input:**
- `command` (string): The oc command to analyze (e.g., "oc get pods -n production")

**Output:**
```json
{
  "status": "success",
  "command": "oc get pods -n production",
  "operation": "get",
  "resource_type": "pods",
  "flags": {
    "-n": "production"
  },
  "namespace": "production",
  "arguments": [],
  "analysis": "This command will retrieve and display pods resource(s) in the 'production' namespace.",
  "recommendations": [
    "Use -o yaml or -o json to get full resource details in structured format",
    "Consider using label selectors (-l) to filter resources precisely"
  ]
}
```

#### 2. get_oc_help

Retrieves help documentation for oc commands.

**Input:**
- `subcommand` (string, optional): Specific oc subcommand to get help for (e.g., "get", "apply")

**Output:**
```json
{
  "status": "success",
  "subcommand": "get",
  "help_text": "...",
  "message": "Help for oc get retrieved successfully"
}
```

#### 3. explain_oc_resource

Get detailed documentation about OpenShift resource types using `oc explain`.

**Input:**
- `resource_type` (string): The resource type to explain (e.g., "pod", "deployment.spec")

**Output:**
```json
{
  "status": "success",
  "resource_type": "pod",
  "explanation": "...",
  "message": "Successfully retrieved documentation for pod"
}
```

## How to Run the Code Locally

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (fast Python package installer and resolver)
- OpenShift CLI (oc) installed for `get_oc_help` and `explain_oc_resource` tools (optional for `analyze_oc_command`)

### Setup

1. **Install uv (if not already installed):**
   ```bash
   # On macOS/Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On MacOS using brew
   brew install uv

   # On Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip:
   pip install uv
   ```

2. **Navigate to the server directory:**
   ```bash
   cd oc-commands-analyzer-mcp-server
   ```

3. **Create and activate a virtual environment with uv:**
   ```bash
   uv venv

   # Activate the virtual environment:
   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

4. **Install the package and dependencies:**
   ```bash
   # Install in editable mode with all dependencies
   uv pip install -e .
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. **Run the server:**
   ```bash
   # Using the installed console script
   oc-commands-analyzer-mcp-server

   # Or directly with Python module
   python -m oc_commands_analyzer_mcp_server.src.main

   # Or using uv to run directly
   uv run python -m oc_commands_analyzer_mcp_server.src.main
   ```

### Configuration Options

The server configuration is managed through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `localhost` | Server bind address |
| `MCP_PORT` | `5002` | Server port (1024-65535) |
| `MCP_TRANSPORT_PROTOCOL` | `http` | Transport protocol (`http`, `sse`, `streamable-http`) |
| `MCP_SSL_KEYFILE` | `None` | SSL private key file path |
| `MCP_SSL_CERTFILE` | `None` | SSL certificate file path |
| `PYTHON_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `COMPATIBLE_WITH_CURSOR` | `True` | Cursor compatibility flag |

### Verify Installation

1. **Health check:**
   ```bash
   curl http://localhost:5002/health
   ```

2. **Test MCP tools:**
   ```bash
   # Test analyze_oc_command tool
   curl -X POST "http://localhost:5002/mcp" \
        -H "Content-Type: application/json" \
        -d '{"method": "tools/call", "params": {"name": "analyze_oc_command", "arguments": {"command": "oc get pods -n production"}}}'
   ```

## How to Test the Code Locally

### Development Environment Setup

1. **Install development dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests (when tests are implemented)
pytest

# Run tests with coverage
pytest --cov=oc_commands_analyzer_mcp_server --cov-report=html --cov-report=term
```

### Code Quality Checks

1. **Linting and formatting with Ruff:**
   ```bash
   # Check for issues
   ruff check .

   # Auto-fix issues
   ruff check . --fix

   # Format code
   ruff format .
   ```

2. **Type checking with MyPy:**
   ```bash
   mypy oc_commands_analyzer_mcp_server/
   ```

## Usage Examples

### Analyzing an OC Command

```python
# Using the MCP tool through an MCP client
result = await mcp_client.call_tool(
    "analyze_oc_command",
    {"command": "oc get deployments -l app=myapp -o yaml"}
)
```

### Getting Help for a Subcommand

```python
result = await mcp_client.call_tool(
    "get_oc_help",
    {"subcommand": "apply"}
)
```

### Explaining a Resource Type

```python
result = await mcp_client.call_tool(
    "explain_oc_resource",
    {"resource_type": "deployment.spec.replicas"}
)
```

## How to Contribute

### Development Workflow

1. **Fork and clone:**
   ```bash
   git clone <your-fork-url>
   cd oc-commands-analyzer-mcp-server
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   pre-commit install
   ```

4. **Make changes following our standards**

5. **Run comprehensive testing:**
   ```bash
   # Code quality
   ruff check . --fix
   ruff format .
   mypy oc_commands_analyzer_mcp_server/

   # Tests
   pytest --cov=oc_commands_analyzer_mcp_server

   # Pre-commit validation
   pre-commit run --all-files
   ```

6. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: descriptive commit message"
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**

### Coding Standards

- **Python Style**: Follow PEP 8 (enforced by Ruff)
- **Type Annotations**: Required for all public functions and methods
- **Documentation**: Google-style docstrings for all public APIs
- **Testing**: Write tests for new functionality with pytest
- **Commits**: Use conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- **Error Handling**: Use structured logging and proper exception handling

### Adding New MCP Tools

1. **Create tool function in `oc_analyzer_tool.py`:**
   ```python
   def your_new_tool(param: str) -> Dict[str, Any]:
       """Your tool description.

       TOOL_NAME=your_new_tool
       DISPLAY_NAME=Your Tool Name
       USECASE=What this tool does

       Args:
           param: Parameter description.

       Returns:
           dict: Result dictionary.
       """
       # Implementation here
       return {"result": "success"}
   ```

2. **Register in MCP server (`mcp.py`):**
   ```python
   from oc_commands_analyzer_mcp_server.src.tools.oc_analyzer_tool import your_new_tool

   def _register_mcp_tools(self) -> None:
       self.mcp.tool()(your_new_tool)  # Add this line
   ```

3. **Add tests and documentation**

## License

Apache 2.0 - See LICENSE file for details

## Support

For issues, questions, or contributions, please visit the project repository or contact the maintainers.
